import{S as e,i as t,s as n,e as s,a,b as r,y as o,d as i,f as l,v as u,k as c}from"./main-ab58c0ec.js";function f(e){let t;return{c(){t=s("a"),t.textContent="logout",r(t,"href","/logout")},m(e,n){i(e,t,n)},d(e){e&&c(t)}}}function d(e){let t;return{c(){t=s("a"),t.textContent="login",r(t,"href","/login")},m(e,n){i(e,t,n)},d(e){e&&c(t)}}}function m(e){let t,n,m,h,p,x;function g(e,t){return"anon"==e[0]?d:f}let v=g(e),j=v(e);return{c(){t=s("nav"),n=s("span"),n.innerHTML='<a href="/">Home</a>',m=a(),h=s("span"),p=s("input"),x=a(),j.c(),r(n,"class","header-left svelte-1j9ezxe"),r(p,"type","text"),o(p,"width","6rem"),r(h,"class","header-right svelte-1j9ezxe"),r(t,"class","header svelte-1j9ezxe")},m(e,s){i(e,t,s),l(t,n),l(t,m),l(t,h),l(h,p),l(h,x),j.m(h,null)},p(e,[t]){v!==(v=g(e))&&(j.d(1),j=v(e),j&&(j.c(),j.m(h,null)))},i:u,o:u,d(e){e&&c(t),j.d()}}}function h(e,t,n){let{user_info:s}=t;return e.$$set=e=>{"user_info"in e&&n(0,s=e.user_info)},[s]}class p extends e{constructor(e){super(),t(this,e,h,m,n,{user_info:0})}}export{p as H};
//# sourceMappingURL=header-b2f88002.js.map
