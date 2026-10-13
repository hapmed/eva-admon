// Auditoría de diseño con Playwright: hace login y captura pantallas en PC y móvil.
// Uso:  ADMON_EMAIL=... ADMON_PASSWORD=... node e2e/audit.mjs
// Opcional: ADMON_URL (por defecto la URL pública), ADMON_SHOTS (carpeta de salida).

import { mkdirSync } from 'node:fs';
import { chromium } from '@playwright/test';

const BASE = process.env.ADMON_URL ?? 'https://admon.hapmed.qzz.io';
const EMAIL = process.env.ADMON_EMAIL;
const PASSWORD = process.env.ADMON_PASSWORD;
const OUT = process.env.ADMON_SHOTS ?? 'e2e/shots';

if (!EMAIL || !PASSWORD) {
	console.error('Faltan ADMON_EMAIL / ADMON_PASSWORD');
	process.exit(1);
}

const viewports = {
	desktop: { width: 1440, height: 900 },
	mobile: { width: 390, height: 844, isMobile: true, deviceScaleFactor: 2 }
};

const routes = [
	['dashboard', '/'],
	['clientes', '/clientes'],
	['cotizaciones', '/cotizaciones'],
	['cotizacion_nueva', '/cotizaciones/nueva', 'cotizacion'],
	['calculos', '/calculos'],
	['calculo_nuevo', '/calculos/nuevo', 'calculo'],
	['configuracion', '/configuracion']
];

mkdirSync(OUT, { recursive: true });

const browser = await chromium.launch();

for (const [vpName, vp] of Object.entries(viewports)) {
	const context = await browser.newContext({
		viewport: { width: vp.width, height: vp.height },
		isMobile: vp.isMobile ?? false,
		deviceScaleFactor: vp.deviceScaleFactor ?? 1
	});
	const page = await context.newPage();

	await page.goto(`${BASE}/login`, { waitUntil: 'networkidle' });
	await page.fill('input[type=email]', EMAIL);
	await page.fill('input[type=password]', PASSWORD);
	await page.click('button[type=submit]');
	await page
		.waitForURL((url) => !url.pathname.startsWith('/login'), { timeout: 20000 })
		.catch(() => {});
	await page.waitForLoadState('networkidle').catch(() => {});

	for (const [name, path, form] of routes) {
		await page.goto(`${BASE}${path}`, { waitUntil: 'networkidle' }).catch(() => {});
		await page.waitForTimeout(900);
		if (form === 'cotizacion') {
			const add = page.getByRole('button', { name: /Línea/i });
			await add.click().catch(() => {});
			await add.click().catch(() => {});
			await page.waitForTimeout(400);
		}
		if (form === 'calculo') {
			const add = page.getByRole('button', { name: /Partida/i });
			await add.click().catch(() => {});
			await add.click().catch(() => {});
			await page.waitForTimeout(400);
		}
		await page.screenshot({ path: `${OUT}/${vpName}_${name}.png`, fullPage: true });
		console.log(`shot ${vpName}_${name}`);
	}
	await context.close();
}

await browser.close();
console.log('done');
