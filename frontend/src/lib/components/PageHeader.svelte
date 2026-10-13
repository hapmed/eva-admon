<script lang="ts">
	import type { Snippet } from 'svelte';

	let { title, subtitle, actions }: { title: string; subtitle?: string; actions?: Snippet } =
		$props();
</script>

<div class="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
	<div>
		<h1 class="text-[28px] font-semibold tracking-tight">{title}</h1>
		{#if subtitle}
			<p class="mt-1 text-[15px] text-ink-2">{subtitle}</p>
		{/if}
	</div>
	{#if actions}
		<div class="flex flex-wrap gap-2 sm:justify-end">{@render actions()}</div>
	{/if}
</div>
