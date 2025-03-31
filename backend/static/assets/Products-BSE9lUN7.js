import{r as n,o as V,c as l,a as e,g as k,e as a,t as m,F as z,d as D,h as L,w as p,i as v,f as i}from"./index-B_mHQNk2.js";import{a as x}from"./api-CN_Fsn29.js";const $={key:0,class:"flex justify-center py-20"},A={key:1,class:"bg-red-50 border-l-4 border-red-400 p-4 mb-6 rounded-r-lg shadow-sm"},F={class:"flex"},H={class:"ml-3"},N={class:"text-sm text-red-700"},U={key:2,class:"bg-white shadow-lg rounded-xl overflow-hidden"},T={key:3,class:"bg-white shadow-lg rounded-xl overflow-hidden"},q={role:"list",class:"divide-y divide-gray-200"},I={class:"flex items-center justify-between"},S={class:"flex items-center"},G={class:"flex-shrink-0 h-14 w-14 bg-gray-100 rounded-lg overflow-hidden shadow-sm"},R=["src","alt","onError"],J={key:1,class:"h-full w-full flex items-center justify-center text-gray-400"},K={class:"ml-4"},O={class:"text-sm font-medium text-primary-600"},Q={class:"flex flex-wrap space-x-4 mt-1"},W={class:"text-sm text-gray-500 flex items-center"},X={class:"flex space-x-2"},Y=["onClick"],Z=["onClick"],ee={key:4,class:"fixed inset-0 overflow-y-auto z-50","aria-labelledby":"modal-title",role:"dialog","aria-modal":"true"},te={class:"flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0"},se={class:"inline-block align-bottom bg-white rounded-xl text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full"},oe={class:"bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4"},re={class:"sm:flex sm:items-start"},le={class:"mt-3 text-center sm:mt-0 sm:text-left w-full"},ie={class:"text-lg leading-6 font-medium text-gray-900",id:"modal-title"},ne={class:"mt-4 space-y-4"},ae={key:0,class:"mt-3 h-32 w-32 rounded-lg overflow-hidden bg-gray-100 shadow-sm"},de=["src"],me={class:"bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse"},ue={type:"submit",class:"w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-primary-600 text-base font-medium text-white hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 sm:ml-3 sm:w-auto sm:text-sm transition-colors duration-150"},ce={key:5,class:"fixed inset-0 overflow-y-auto z-50","aria-labelledby":"modal-title",role:"dialog","aria-modal":"true"},fe={class:"flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0"},ge={class:"inline-block align-bottom bg-white rounded-xl text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full"},pe={class:"bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4"},ve={class:"sm:flex sm:items-start"},xe={class:"mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left"},we={class:"mt-2"},ye={class:"text-sm text-gray-500"},be={class:"font-medium"},he={class:"bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse"},je={__name:"Products",setup(ke){const w=n([]),y=n(!0),u=n(null),d=n(!1),c=n(!1),f=n(!1),g=n(null),r=n({id:null,name:"",description:"",cost_price:0,image_url:""}),_=o=>{o.target.src="/placeholder-image.png"},b=async()=>{y.value=!0;try{const o=await x.getProducts();w.value=o.data}catch(o){console.error("Error fetching products:",o),u.value="Failed to load products. Please try again later."}finally{y.value=!1}},C=()=>{f.value=!1,r.value={id:null,name:"",description:"",cost_price:0,image_url:""},d.value=!0},M=o=>{f.value=!0,r.value={id:o.id,name:o.name,description:o.description||"",cost_price:o.cost_price,image_url:o.image_url||""},d.value=!0},P=async()=>{try{f.value?await x.updateProduct(r.value.id,r.value):await x.createProduct(r.value),d.value=!1,await b()}catch(o){console.error("Error saving product:",o),u.value="Failed to save product. Please try again."}},B=o=>{g.value=o,c.value=!0},E=async()=>{if(g.value)try{await x.deleteProduct(g.value.id),c.value=!1,await b()}catch(o){console.error("Error deleting product:",o),u.value="Failed to delete product. Please try again."}};return V(b),(o,t)=>{var j;return i(),l("div",null,[e("div",{class:"flex justify-between items-center mb-6"},[t[10]||(t[10]=e("h1",{class:"text-2xl font-semibold text-gray-900"},"Products",-1)),e("button",{onClick:C,class:"inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors duration-150"},t[9]||(t[9]=[e("svg",{xmlns:"http://www.w3.org/2000/svg",class:"h-5 w-5 mr-1.5",fill:"none",viewBox:"0 0 24 24",stroke:"currentColor"},[e("path",{"stroke-linecap":"round","stroke-linejoin":"round","stroke-width":"2",d:"M12 4v16m8-8H4"})],-1),a(" Add Product ")]))]),y.value?(i(),l("div",$,t[11]||(t[11]=[e("div",{class:"animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"},null,-1)]))):u.value?(i(),l("div",A,[e("div",F,[t[12]||(t[12]=e("div",{class:"flex-shrink-0"},[e("svg",{class:"h-5 w-5 text-red-400",xmlns:"http://www.w3.org/2000/svg",viewBox:"0 0 20 20",fill:"currentColor"},[e("path",{"fill-rule":"evenodd",d:"M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z","clip-rule":"evenodd"})])],-1)),e("div",H,[e("p",N,m(u.value),1)])])])):w.value.length===0?(i(),l("div",U,[e("div",{class:"px-6 py-8 text-center"},[t[14]||(t[14]=e("svg",{xmlns:"http://www.w3.org/2000/svg",class:"h-16 w-16 mx-auto text-gray-400 mb-4",fill:"none",viewBox:"0 0 24 24",stroke:"currentColor"},[e("path",{"stroke-linecap":"round","stroke-linejoin":"round","stroke-width":"2",d:"M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"})],-1)),t[15]||(t[15]=e("h3",{class:"text-lg leading-6 font-medium text-gray-900 mb-2"},"No products found",-1)),t[16]||(t[16]=e("div",{class:"mt-2 max-w-xl text-sm text-gray-500 mx-auto mb-6"},[e("p",null,"Get started by adding your first product.")],-1)),e("button",{onClick:C,class:"inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors duration-150"},t[13]||(t[13]=[e("svg",{xmlns:"http://www.w3.org/2000/svg",class:"h-5 w-5 mr-1.5",fill:"none",viewBox:"0 0 24 24",stroke:"currentColor"},[e("path",{"stroke-linecap":"round","stroke-linejoin":"round","stroke-width":"2",d:"M12 4v16m8-8H4"})],-1),a(" Add Product ")]))])])):(i(),l("div",T,[e("ul",q,[(i(!0),l(z,null,D(w.value,s=>(i(),l("li",{key:s.id,class:"px-6 py-5 hover:bg-gray-50 transition-colors duration-150"},[e("div",I,[e("div",S,[e("div",G,[s.image_url?(i(),l("img",{key:0,src:s.image_url,alt:s.name,class:"h-full w-full object-cover",onError:h=>_(h)},null,40,R)):(i(),l("div",J,t[17]||(t[17]=[e("svg",{xmlns:"http://www.w3.org/2000/svg",class:"h-6 w-6",fill:"none",viewBox:"0 0 24 24",stroke:"currentColor"},[e("path",{"stroke-linecap":"round","stroke-linejoin":"round","stroke-width":"2",d:"M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"})],-1)])))]),e("div",K,[e("p",O,m(s.name),1),e("div",Q,[e("p",W,[t[18]||(t[18]=e("svg",{xmlns:"http://www.w3.org/2000/svg",class:"h-4 w-4 mr-1 text-gray-400",fill:"none",viewBox:"0 0 24 24",stroke:"currentColor"},[e("path",{"stroke-linecap":"round","stroke-linejoin":"round","stroke-width":"2",d:"M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"})],-1)),a(" $"+m(s.cost_price.toFixed(2)),1)])])])]),e("div",X,[e("button",{onClick:h=>M(s),class:"inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors duration-150"},t[19]||(t[19]=[e("svg",{xmlns:"http://www.w3.org/2000/svg",class:"h-4 w-4 mr-1",fill:"none",viewBox:"0 0 24 24",stroke:"currentColor"},[e("path",{"stroke-linecap":"round","stroke-linejoin":"round","stroke-width":"2",d:"M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"})],-1),a(" Edit ")]),8,Y),e("button",{onClick:h=>B(s),class:"inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded-md text-gray-700 bg-white hover:bg-red-50 hover:text-red-700 hover:border-red-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-colors duration-150"},t[20]||(t[20]=[e("svg",{xmlns:"http://www.w3.org/2000/svg",class:"h-4 w-4 mr-1",fill:"none",viewBox:"0 0 24 24",stroke:"currentColor"},[e("path",{"stroke-linecap":"round","stroke-linejoin":"round","stroke-width":"2",d:"M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"})],-1),a(" Delete ")]),8,Z)])])]))),128))])])),d.value?(i(),l("div",ee,[e("div",te,[e("div",{class:"fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity","aria-hidden":"true",onClick:t[0]||(t[0]=s=>d.value=!1)}),t[25]||(t[25]=e("span",{class:"hidden sm:inline-block sm:align-middle sm:h-screen","aria-hidden":"true"},"​",-1)),e("div",se,[e("form",{onSubmit:L(P,["prevent"])},[e("div",oe,[e("div",re,[e("div",le,[e("h3",ie,m(f.value?"Edit Product":"Add New Product"),1),e("div",ne,[e("div",null,[t[21]||(t[21]=e("label",{for:"name",class:"block text-sm font-medium text-gray-700"},"Product Name",-1)),p(e("input",{type:"text",name:"name",id:"name","onUpdate:modelValue":t[1]||(t[1]=s=>r.value.name=s),class:"mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md",required:""},null,512),[[v,r.value.name]])]),e("div",null,[t[22]||(t[22]=e("label",{for:"cost_price",class:"block text-sm font-medium text-gray-700"},"Cost Price ($)",-1)),p(e("input",{type:"number",name:"cost_price",id:"cost_price","onUpdate:modelValue":t[2]||(t[2]=s=>r.value.cost_price=s),min:"0",step:"0.01",class:"mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md",required:""},null,512),[[v,r.value.cost_price]])]),e("div",null,[t[23]||(t[23]=e("label",{for:"description",class:"block text-sm font-medium text-gray-700"},"Description",-1)),p(e("textarea",{id:"description",name:"description",rows:"3","onUpdate:modelValue":t[3]||(t[3]=s=>r.value.description=s),class:"shadow-sm focus:ring-primary-500 focus:border-primary-500 mt-1 block w-full sm:text-sm border border-gray-300 rounded-md"},null,512),[[v,r.value.description]])]),e("div",null,[t[24]||(t[24]=e("label",{for:"image_url",class:"block text-sm font-medium text-gray-700"},"Image URL",-1)),p(e("input",{type:"url",name:"image_url",id:"image_url","onUpdate:modelValue":t[4]||(t[4]=s=>r.value.image_url=s),placeholder:"https://example.com/image.jpg",class:"mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"},null,512),[[v,r.value.image_url]]),r.value.image_url?(i(),l("div",ae,[e("img",{src:r.value.image_url,class:"h-full w-full object-cover",onError:t[5]||(t[5]=s=>_(s))},null,40,de)])):k("",!0)])])])])]),e("div",me,[e("button",ue,m(f.value?"Update":"Add"),1),e("button",{type:"button",onClick:t[6]||(t[6]=s=>d.value=!1),class:"mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm transition-colors duration-150"}," Cancel ")])],32)])])])):k("",!0),c.value?(i(),l("div",ce,[e("div",fe,[e("div",{class:"fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity","aria-hidden":"true",onClick:t[7]||(t[7]=s=>c.value=!1)}),t[30]||(t[30]=e("span",{class:"hidden sm:inline-block sm:align-middle sm:h-screen","aria-hidden":"true"},"​",-1)),e("div",ge,[e("div",pe,[e("div",ve,[t[29]||(t[29]=e("div",{class:"mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-red-100 sm:mx-0 sm:h-10 sm:w-10"},[e("svg",{class:"h-6 w-6 text-red-600",xmlns:"http://www.w3.org/2000/svg",fill:"none",viewBox:"0 0 24 24",stroke:"currentColor","aria-hidden":"true"},[e("path",{"stroke-linecap":"round","stroke-linejoin":"round","stroke-width":"2",d:"M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"})])],-1)),e("div",xe,[t[28]||(t[28]=e("h3",{class:"text-lg leading-6 font-medium text-gray-900",id:"modal-title"}," Delete Product ",-1)),e("div",we,[e("p",ye,[t[26]||(t[26]=a(" Are you sure you want to delete ")),e("span",be,m((j=g.value)==null?void 0:j.name),1),t[27]||(t[27]=a("? This action cannot be undone. "))])])])])]),e("div",he,[e("button",{type:"button",onClick:E,class:"w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-red-600 text-base font-medium text-white hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 sm:ml-3 sm:w-auto sm:text-sm transition-colors duration-150"}," Delete "),e("button",{type:"button",onClick:t[8]||(t[8]=s=>c.value=!1),class:"mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm transition-colors duration-150"}," Cancel ")])])])])):k("",!0)])}}};export{je as default};
