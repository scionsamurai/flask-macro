function e(e){const t=t=>{!e||e.contains(t.target)||t.defaultPrevented||e.dispatchEvent(new CustomEvent("click_outside",e))};return document.addEventListener("click",t,!0),{destroy(){document.removeEventListener("click",t,!0)}}}export{e as c};
//# sourceMappingURL=clickOutside-3df9c706.js.map
