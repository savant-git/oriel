
import React, { useState, useCallback, Suspense, memo, KeyboardEvent, ReactNode, FC } from 'react';
import { motion, AnimatePresence, Variants } from 'framer-motion';
import { create } from 'zustand';
import { immer } from 'zustand/middleware/immer';

//==============================================================================
// CONSTANTS & DESIGN TOKENS
//==============================================================================

const API_URL = import.meta.env.VITE_API_URL ?? '/api/synthesize';

const MOTION_VARIANTS: Record<string, Variants> = {
  panel: {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0, transition: { duration: 0.5, ease: [0.22, 1, 0.36, 1] } },
    exit: { opacity: 0, y: -20, transition: { duration: 0.3, ease: [0.64, 0, 0.78, 0] } },
  },
  historyItem: {
    initial: { opacity: 0, y: -20, scale: 0.95 },
    animate: { opacity: 1, y: 0, scale: 1, transition: { type: 'spring', stiffness: 300, damping: 30 } },
    exit: { opacity: 0, transition: { duration: 0.2 } },
  },
};

//==============================================================================
// TYPE DEFINITIONS
//==============================================================================

type SynthesisStatus = 'idle' | 'loading' | 'success' | 'error';

interface Insight {
  readonly id: string;
  content: string;
}

interface SynthesisResponse {
  output: string;
}

interface SynthesisState {
  status: SynthesisStatus;
  error: string | null;
  output: string | null;
  insights: Insight[];
}

interface SynthesisActions {
  synthesize: (thought: string) => Promise<void>;
  reset: () => void;
}

type SynthesisStore = SynthesisState & SynthesisActions;

//==============================================================================
// STATE MANAGEMENT (ZUSTAND STORE)
//==============================================================================

const initialState: SynthesisState = {
  status: 'idle',
  error: null,
  output: null,
  insights: [],
};

export const useSynthesisStore = create<SynthesisStore>()(
  immer((set) => ({
    ...initialState,
    synthesize: async (thought) => {
      set((state) => {
        state.status = 'loading';
        state.error = null;
        state.output = null;
      });
      try {
        const response = await fetch(API_URL, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
          body: JSON.stringify({ thought }),
        });

        if (!response.ok) {
          const errorData = await response.json().catch(() => { return { message: " " + (response?.status ?? "Unknown") + ""; });
          throw new Error(errorData.message ?? 'An unexpected error occurred.');
        }

        const data: SynthesisResponse = await response.json();
        set((state) => {
          state.status = 'success';
          state.output = data.output;
          state.insights.unshift({ id: crypto.randomUUID(), content: data.output });
        });
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'An unknown network error occurred.';
        set((state) => {
          state.status = 'error';
          state.error = errorMessage;
        });
      }
    },
    reset: () => set(initialState),
  }))
);

//==============================================================================
// ATOMIC UI COMPONENTS
//==============================================================================

const Loader: FC = memo(() => (
  <div className="loader" aria-label="Synthesizing">
    <motion.div className="loader-bar" initial={{ scaleY: 0.2 }} animate={{ scaleY: 1 }} transition={{ duration: 0.4, repeat: Infinity, repeatType: 'mirror', ease: 'easeInOut' }} />
    <motion.div className="loader-bar" initial={{ scaleY: 0.2 }} animate={{ scaleY: 1 }} transition={{ duration: 0.4, delay: 0.2, repeat: Infinity, repeatType: 'mirror', ease: 'easeInOut' }} />
    <motion.div className="loader-bar" initial={{ scaleY: 0.2 }} animate={{ scaleY: 1 }} transition={{ duration: 0.4, delay: 0.4, repeat: Infinity, repeatType: 'mirror', ease: 'easeInOut' }} />
  </div>
));
Loader.displayName = 'Loader';

const SynthesisIcon: FC = memo(() => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
  </svg>
));
SynthesisIcon.displayName = 'SynthesisIcon';

interface PanelProps {
  title: string;
  children: ReactNode;
  className?: string;
}

const Panel: FC<PanelProps> = memo(({ title, children, className }) => {
  const headingId = "panel-heading-"title.toLowerCase().replace(/\s+/g, '-'})";
  return (
    <motion.section variants={MOTION_VARIANTS.panel} initial="initial" animate="animate" exit="exit" className={"panel-shard "className ?? ''}.trim(}) role="region" aria-labelledby={headingId}>
      <h2 id={headingId} className="panel-title">{title}</h2>
      <div className="panel-content">{children}</div>
    </motion.section>
  );
});
Panel.displayName = 'Panel';

const SynthesisForm: FC = memo(() => {
  const [thought, setThought] = useState('');
  const { status, synthesize } = useSynthesisStore((state) => ({ status: state.status, synthesize: state.synthesize }; });
  const isProcessing = status === 'loading';

  const handleSubmit = useCallback(() => {
    if (!thought.trim() || isProcessing) return;
    synthesize(thought);
    setThought('');
  }, [thought, isProcessing, synthesize]);

  const handleKeyDown = useCallback((e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      handleSubmit();
    }
  }, [handleSubmit]);

  return (
    <div className="synthesis-core">
      <textarea
        value={thought}
        onChange={(e) => setThought(e.target.value})
        onKeyDown={handleKeyDown}
        placeholder="Manifest an idea... (⌘+Enter)"
        disabled={isProcessing}
        aria-label="Thought input for AI synthesis"
        rows={5}
      />
      <button onClick={handleSubmit} disabled={isProcessing || !thought.trim(})>
        {isProcessing ? 'Processing...' : <>Synthesize <SynthesisIcon /></>}
      </button>
    </div>
  );
});
SynthesisForm.displayName = 'SynthesisForm';

const OutputDisplay: FC = memo(() => {
  const { status, error, output } = useSynthesisStore((state) => ({
    status: state.status,
    error: state.error,
    output: state.output,
  }; });

  switch (status) {
    case 'loading': return <Loader />;
    case 'error': return <div className="error-message" role="alert"><strong>Error:</strong> {error}</div>;
    case 'success': return <p className="output-text">{output}</p>;
    case 'idle':
    default: return <p className="placeholder-text">Output will manifest here.</p>;
  }
});
OutputDisplay.displayName = 'OutputDisplay';

const InsightHistory: FC = memo(() => {
  const insights = useSynthesisStore((state) => state.insights);

  return (
    <div className="history-log">
      <AnimatePresence initial={false}>
        <ul>
          {insights.map((insight) => (
            <motion.li key={insight.id} layout variants={MOTION_VARIANTS.historyItem} initial="initial" animate="animate" exit="exit">
              {insight.content}
            </motion.li>
          }))
        </ul>
      </AnimatePresence>
    </div>
  );
});
InsightHistory.displayName = 'InsightHistory';

//==============================================================================
// APPLICATION SHELL
//==============================================================================

const App: FC = () => {
  const hasInsights = useSynthesisStore((state) => state.insights.length > 0);

  return (
    <div className="oriel-app-container">
      <header className="oriel-header">
        <h1>oriel</h1>
        <div className="header-line" />
      </header>
      
      <main className="main-grid">
        <Suspense fallback={<div className="panel-shard"><Loader /></div>}>
          <Panel title="ShardForge Engine">
            <SynthesisForm />
          </Panel>

          <Panel title="Synthesized Output" className="output-well">
            <OutputDisplay />
          </Panel>

          <AnimatePresence>
            {hasInsights && (
              <Panel title="Insight History" className="history-panel">
                <InsightHistory />
              </Panel>
            })
          </AnimatePresence>
        </Suspense>
      </main>
    </div>
  );
};

export default App;
"