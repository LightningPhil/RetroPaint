const preview=location.pathname.includes('/tests/')||new URLSearchParams(location.search).has('layout-preview');
function storage():Storage {return preview?sessionStorage:localStorage;}
export function readPreference(key:string):string|null {try{return storage().getItem(key);}catch{return null;}}
export function writePreference(key:string,value:string):void {try{storage().setItem(key,value);}catch{/* Preferences still work for the current visit. */}}
