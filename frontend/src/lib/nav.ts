import type { Component } from 'svelte';
import {
	Calculator,
	FileText,
	LayoutDashboard,
	Package,
	Settings,
	UserCog,
	Users,
	Wrench
} from '@lucide/svelte';
import type { Rol } from './auth';

export type NavItem = { href: string; label: string; icon: Component; roles?: Rol[] };
export type NavGroup = { label: string; items: NavItem[] };

export const navGroups: NavGroup[] = [
	{
		label: 'General',
		items: [{ href: '/', label: 'Dashboard', icon: LayoutDashboard }]
	},
	{
		label: 'Catálogos',
		items: [
			{ href: '/clientes', label: 'Clientes', icon: Users },
			{ href: '/servicios', label: 'Servicios', icon: Wrench },
			{ href: '/materiales', label: 'Materiales', icon: Package }
		]
	},
	{
		label: 'Cotizaciones',
		items: [
			{ href: '/cotizaciones', label: 'Cotizaciones', icon: FileText },
			{ href: '/calculos', label: 'Cálculos', icon: Calculator }
		]
	},
	{
		label: 'Administración',
		items: [
			{ href: '/usuarios', label: 'Usuarios', icon: UserCog, roles: ['admin'] },
			{ href: '/configuracion', label: 'Configuración', icon: Settings, roles: ['admin'] }
		]
	}
];
