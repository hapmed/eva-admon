import adapter from '@sveltejs/adapter-static';
import { sveltekit } from '@sveltejs/kit/vite';
import tailwindcss from '@tailwindcss/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	server: {
		proxy: {
			'/api': 'http://localhost:8000'
		}
	},
	plugins: [
		tailwindcss(),
		sveltekit({
			compilerOptions: {
				// Fuerza el modo runes en el proyecto, excepto en librerías. Puede quitarse en Svelte 6.
				runes: ({ filename }) =>
					filename.split(/[/\\]/).includes('node_modules') ? undefined : true
			},
			// SPA: un solo artefacto estático que sirve el backend (una imagen, un puerto).
			adapter: adapter({ fallback: 'index.html' })
		})
	]
});
