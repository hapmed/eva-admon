<script lang="ts">
	import { page } from '$app/state';
	import CalculoForm from '../../../../lib/components/CalculoForm.svelte';

	const calculoId = Number(page.params.id);
</script>

<CalculoForm {calculoId} />
