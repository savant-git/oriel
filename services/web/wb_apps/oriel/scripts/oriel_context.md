```typescript
import { create } from 'zustand';
import { immer } from 'zustand/middleware/immer';
import { v4 as uuidv4 } from 'uuid';

// --- CORE DOMAIN TYPES ---

export type orielEngineId = 'SHARD_ENGINE' | 'MOOD_ENGINE' | 'TIMELINE_ENGINE' | 'SIMULATION_ENGINE' | 'WORLD_BUILDER';
export type orielMode = 'FICTION' | 'NONFICTION';
export type ShardType = 'Character' | 'Location' | 'Object' | 'Event' | 'Lore';

export interface Vector3Data {
  x: number;
  y: number;
  z: number;
}

export interface Shard {
  readonly id: string;
  type: ShardType;
  title: string;
  content: string;
  metadata: Record<string, unknown>;
  position: Vector3Data;
  connections: readonly string[]; // Array of Shard IDs
  readonly createdAt: string;
  updatedAt: string;
}

export interface Mood {
  readonly id: string;
  name: string;
  color: string; // Hex code
  intensity: number; // 0.0 to 1.0
  influenceRadius: number;
  position: Vector3Data;
}

export interface TimelineEvent {
  readonly id: string;
  timestamp: number;
  description: string;
  linkedShards: readonly string[]; // Array of Shard IDs
}

export interface CreativeSystem {
  readonly id: string;
  title: string;
  shards: ReadonlyMap<string, Shard>;
  moods: ReadonlyMap<string, Mood>;
  timeline: readonly TimelineEvent[];
}

// --- UI & SYSTEM STATE ---

export interface SystemState {
  readonly systemId: string;
  readonly version: string;
  isInitialized: boolean;
  activeMode: orielMode;
  activeEngine: orielEngineId | null;
  isLoading: boolean;
  error: string | null;
}

export interface UIState {
  activeShardId: string | null;
  selectedShardIds: ReadonlySet<string>;
  cameraFocusTarget: Vector3Data | null;
  isCommandPaletteOpen: boolean;
}

// --- ZUSTAND STORE DEFINITION ---

export interface orielState {
  readonly system: SystemState;
  readonly ui: UIState;
  readonly project: CreativeSystem;
}

// --- ACTION PAYLOAD TYPES ---

export type CreateShardPayload = {
  type: ShardType;
  title: string;
  content?: string;
  position?: Vector3Data;
};
export type UpdateShardPayload = Partial<Omit<Shard, 'id' | 'createdAt' | 'updatedAt'>>;

export type CreateMoodPayload = {
  name: string;
  color: string;
  intensity: number;
  position: Vector3Data;
  influenceRadius?: number;
};
export type UpdateMoodPayload = Partial<Omit<Mood, 'id'>>;

export interface orielActions {
  // System Actions
  initializeSystem: (mode: orielMode, projectTitle: string) => void;
  setMode: (mode: orielMode) => void;
  setActiveEngine: (engine: orielEngineId | null) => void;
  setError: (error: string | null) => void;
  setLoading: (isLoading: boolean) => void;

  // Project & Shard Actions
  createShard: (payload: CreateShardPayload) => string;
  updateShard: (shardId: string, payload: UpdateShardPayload) => void;
  deleteShard: (shardId: string) => void;
  connectShards: (sourceId: string, targetId: string) => void;
  disconnectShards: (sourceId: string, targetId: string) => void;

  // Mood Actions
  createMood: (payload: CreateMoodPayload) => string;
  updateMood: (moodId: string, payload: UpdateMoodPayload) => void;
  deleteMood: (moodId: string) => void;

  // UI Actions
  selectShard: (shardId: string | null, multiSelect?: boolean) => void;
  clearSelection: () => void;
  setCameraFocus: (position: Vector3Data | null) => void;
  toggleCommandPalette: (isOpen?: boolean) => void;
}

const initialCreativeSystem: CreativeSystem = {
  id: 'UNINITIALIZED',
  title: 'Untitled System',
  shards: new Map(),
  moods: new Map(),
  timeline: [],
};

const initialState: orielState = {
  system: {
    systemId: 'oriel_V2.0',
    version: '2.0.0',
    isInitialized: false,
    activeMode: 'FICTION',
    activeEngine: null,
    isLoading: true,
    error: null,
  },
  ui: {
    activeShardId: null,
    selectedShardIds: new Set(),
    cameraFocusTarget: null,
    isCommandPaletteOpen: false,
  },
  project: initialCreativeSystem,
};

export const useorielStore = create<orielState & orielActions>()(
  immer((set) => ({
    ...initialState,

    // --- System Actions ---
    initializeSystem: (mode, projectTitle) => {
      set((state) => {
        state.system.isInitialized = true;
        state.system.isLoading = false;
        state.system.activeMode = mode;
        state.project = {
            ...initialCreativeSystem,
            id: uuidv4(),
            title: projectTitle,
        };
        state.ui = initialState.ui;
      });
    },
    setMode: (mode) => set((state) => { state.system.activeMode = mode; }),
    setActiveEngine: (engine) => set((state) => { state.system.activeEngine = engine; }),
    setError: (error) => set((state) => { state.system.error = error; }),
    setLoading: (isLoading) => set((state) => { state.system.isLoading = isLoading; }),

    // --- Project & Shard Actions ---
    createShard: (payload) => {
      const newShard: Shard = {
        id: uuidv4(),
        type: payload.type,
        title: payload.title,
        content: payload.content ?? '',
        position: payload.position ?? { x: 0, y: 0, z: 0 },
        metadata: {},
        connections: [],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };
      set((state) => {
        (state.project.shards as Map<string, Shard>).set(newShard.id, newShard);
      });
      return newShard.id;
    },
    updateShard: (shardId, updates) => {
      set((state) => {
        const shard = (state.project.shards as Map<string, Shard>).get(shardId);
        if (shard) {
          Object.assign(shard, updates);
          shard.updatedAt = new Date().toISOString();
        }
      });
    },
    deleteShard: (shardId) => {
      set((state) => {
        (state.project.shards as Map<string, Shard>).delete(shardId);
        state.project.shards.forEach((shard) => {
          (shard.connections as string[]) = shard.connections.filter(id => id !== shardId);
        });
        if (state.ui.activeShardId === shardId) {
          state.ui.activeShardId = null;
        }
        (state.ui.selectedShardIds as Set<string>).delete(shardId);
      });
    },
    connectShards: (sourceId, targetId) => {
      set((state) => {
        const source = (state.project.shards as Map<string, Shard>).get(sourceId);
        const target = state.project.shards.get(targetId);
        if (source && target && !source.connections.includes(targetId)) {
          (source.connections as string[]).push(targetId);
        }
      });
    },
    disconnectShards: (sourceId, targetId) => {
        set((state) => {
            const source = (state.project.shards as Map<string, Shard>).get(sourceId);
            if (source) {
                (source.connections as string[]) = source.connections.filter(id => id !== targetId);
            }
        });
    },

    // --- Mood Actions ---
    createMood: (payload) => {
      const newMood: Mood = {
        id: uuidv4(),
        name: payload.name,
        color: payload.color,
        intensity: payload.intensity,
        position: payload.position,
        influenceRadius: payload.influenceRadius ?? 10.0,
      };
      set((state) => {
        (state.project.moods as Map<string, Mood>).set(newMood.id, newMood);
      });
      return newMood.id;
    },
    updateMood: (moodId, updates) => {
      set((state) => {
        const mood = (state.project.moods as Map<string, Mood>).get(moodId);
        if (mood) {
          Object.assign(mood, updates);
        }
      });
    },
    deleteMood: (moodId) => {
      set((state) => {
        (state.project.moods as Map<string, Mood>).delete(moodId);
      });
    },

    // --- UI Actions ---
    selectShard: (shardId, multiSelect = false) => {
      set((state) => {
        if (!shardId) {
          state.ui.activeShardId = null;
          (state.ui.selectedShardIds as Set<string>).clear();
          return;
        }

        state.ui.activeShardId = shardId;
        if (!multiSelect) {
          (state.ui.selectedShardIds as Set<string>).clear();
        }
        (state.ui.selectedShardIds as Set<string>).add(shardId);
      });
    },
    clearSelection: () => {
      set((state) => {
        state.ui.activeShardId = null;
        (state.ui.selectedShardIds as Set<string>).clear();
      });
    },
    setCameraFocus: (position) => {
      set((state) => {
        state.ui.cameraFocusTarget = position;
      });
    },
    toggleCommandPalette: (isOpen) => {
      set((state) => {
        state.ui.isCommandPaletteOpen = isOpen ?? !state.ui.isCommandPaletteOpen;
      });
    },
  }))
);
```