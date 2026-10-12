<script lang="ts">
	import { page } from '$app/state';
	import CotizacionForm from '../../../../lib/components/CotizacionForm.svelte';

	const cotizacionId = Number(page.params.id);
</script>

<CotizacionForm {cotizacionId} />
