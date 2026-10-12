export type Page<T> = {
	items: T[];
	total: number;
	page: number;
	page_size: number;
	pages: number;
};
