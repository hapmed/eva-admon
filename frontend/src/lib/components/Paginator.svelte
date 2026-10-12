<script lang="ts">
	let {
		page,
		pages,
		total,
		onPage
	}: { page: number; pages: number; total: number; onPage: (page: number) => void } = $props();

	const buttonClass =
		'inline-flex min-h-9 items-center rounded-[10px] px-3 text-[13px] font-medium transition-colors';
</script>

<div class="flex flex-wrap items-center justify-between gap-2 text-[13px] text-ink-2">
	<span>{total} registro{total === 1 ? '' : 's'}</span>
	<div class="flex items-center gap-2">
		<button
			type="button"
			class="{buttonClass} {page <= 1 ? 'pointer-events-none opacity-50' : 'hover:bg-surface-2'}"
			disabled={page <= 1}
			onclick={() => onPage(page - 1)}
		>
			‹ Anterior
		</button>
		<span>Página {page} de {Math.max(pages, 1)}</span>
		<button
			type="button"
			class="{buttonClass} {page >= pages
				? 'pointer-events-none opacity-50'
				: 'hover:bg-surface-2'}"
			disabled={page >= pages}
			onclick={() => onPage(page + 1)}
		>
			Siguiente ›
		</button>
	</div>
</div>
