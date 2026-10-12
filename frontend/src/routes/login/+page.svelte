<script lang="ts">
	import { goto } from '$app/navigation';
	import { api, ApiError } from '../../lib/api/client';
	import { setSession, type User } from '../../lib/auth';
	import Button from '../../lib/components/Button.svelte';

	let email = $state('');
	let password = $state('');
	let error = $state('');
	let loading = $state(false);

	const inputClass = 'min-h-11 w-full rounded-[12px] border border-line bg-bg px-3 text-[15px]';

	async function submit(event: SubmitEvent) {
		event.preventDefault();
		error = '';
		loading = true;
		try {
			const result = await api.post<{ access_token: string; user: User }>('/auth/login', {
				email,
				password
			});
			setSession(result.access_token, result.user);
			await goto('/');
		} catch (err) {
			error =
				err instanceof ApiError && err.status === 401
					? 'Correo o contraseña incorrectos.'
					: 'No se pudo iniciar sesión. Intenta de nuevo.';
		} finally {
			loading = false;
		}
	}
</script>

<div class="flex min-h-dvh items-center justify-center px-4">
	<div class="w-full max-w-sm rounded-brand-lg border border-line bg-surface p-8 shadow-sm">
		<div class="flex flex-col items-center gap-2">
			<img src="/brand/logo-mark.png" alt="" class="h-12 w-12" />
			<span class="text-[20px] font-bold tracking-[0.18em]">HAPMED</span>
			<p class="text-[14px] text-ink-2">Acceso al sistema</p>
		</div>

		<form class="mt-6 flex flex-col gap-4" onsubmit={submit}>
			<label class="flex flex-col gap-1 text-[14px]">
				<span class="text-ink-2">Correo electrónico</span>
				<input
					class={inputClass}
					type="email"
					autocomplete="username"
					bind:value={email}
					required
				/>
			</label>
			<label class="flex flex-col gap-1 text-[14px]">
				<span class="text-ink-2">Contraseña</span>
				<input
					class={inputClass}
					type="password"
					autocomplete="current-password"
					bind:value={password}
					required
				/>
			</label>

			{#if error}
				<p
					role="alert"
					class="rounded-[12px] border border-danger/40 bg-danger/10 px-3 py-2 text-[14px] text-danger"
				>
					{error}
				</p>
			{/if}

			<Button variant="primary" type="submit" disabled={loading}>
				{loading ? 'Entrando…' : 'Entrar'}
			</Button>
		</form>
	</div>
</div>
