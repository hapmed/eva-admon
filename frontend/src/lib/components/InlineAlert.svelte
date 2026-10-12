<script lang="ts">
	import type { Snippet } from 'svelte';

	type Tone = 'info' | 'success' | 'warning' | 'error';

	let { tone = 'info', children }: { tone?: Tone; children: Snippet } = $props();

	const tones: Record<Tone, string> = {
		info: 'border-line bg-surface-2 text-ink-2',
		success: 'border-success/40 bg-success/10 text-success',
		warning: 'border-warning/40 bg-warning/10 text-warning',
		error: 'border-danger/40 bg-danger/10 text-danger'
	};
</script>

<div role="status" class="rounded-[12px] border px-3 py-2 text-[14px] {tones[tone]}">
	{@render children()}
</div>
