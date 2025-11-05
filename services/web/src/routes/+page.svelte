<script>
  import { onMount } from "svelte";
  let ready = false;
  onMount(()=>{ ready=true; });
</script>

<main class="flex flex-col items-center justify-center min-h-screen bg-gunmetal text-gold">
  <h1 class="text-4xl font-mono mb-4">Savant Development Dashboard</h1>
  <p class="opacity-70">Fractal Core initialized · AI Gateway linked</p>
  {#if !ready}
    <p class="mt-4 animate-pulse text-gold-dark">Initializing…</p>
  {:else}
    <div class="mt-6 p-4 border border-gold-dark rounded-xl shadow-glow">
      <p class="text-sm">Dashboard running in static SvelteKit mode.</p>
    </div>
  {/if}
</main>
