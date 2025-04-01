import{u as Q,r as f,o as T,c as a,a as t,h as D,t as d,F as k,d as R,i as G,w as V,v as O,j as I,b as W,f as n}from"./index-BcK5R-AR.js";import{a as v}from"./api-3vdOSv5H.js";const z={key:0,class:"flex justify-center"},H={key:1,class:"bg-red-50 border-l-4 border-red-400 p-4 mb-4"},J={class:"flex"},K={class:"ml-3"},X={class:"text-sm text-red-700"},Y={key:2,class:"bg-white shadow overflow-hidden sm:rounded-lg"},Z={key:3,class:"bg-white shadow overflow-hidden sm:rounded-lg"},tt={role:"list",class:"divide-y divide-gray-200"},et={class:"flex items-center justify-between"},st={class:"flex-1 min-w-0"},ot={class:"text-sm font-medium text-primary-600 truncate"},it={class:"text-sm text-gray-500"},at={class:"ml-4 flex-shrink-0 flex space-x-2"},nt=["onClick"],rt=["onClick"],dt={key:4,class:"fixed inset-0 overflow-y-auto","aria-labelledby":"modal-title",role:"dialog","aria-modal":"true"},lt={class:"flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0"},ct={class:"inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full"},mt={class:"bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4"},ut={class:"sm:flex sm:items-start"},vt={class:"mt-3 text-center sm:mt-0 sm:text-left w-full"},ft={class:"text-lg leading-6 font-medium text-gray-900",id:"modal-title"},pt={class:"mt-4 space-y-4"},gt=["value"],xt={key:0},yt={class:"space-y-4"},ht={class:"flex justify-between items-center mb-2"},_t={class:"text-sm font-medium text-gray-900"},bt={class:"text-sm text-gray-500"},wt={class:"space-y-2"},kt={key:0,class:"text-sm text-gray-500 italic p-2 text-center"},Rt={class:"col-span-1 text-sm font-medium text-gray-900"},Vt={class:"col-span-1"},Et=["onUpdate:modelValue"],Ct={class:"col-span-1"},Dt=["onUpdate:modelValue"],It={class:"col-span-1 text-sm text-gray-500"},Mt={class:"bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse"},Nt={key:5,class:"fixed inset-0 overflow-y-auto","aria-labelledby":"modal-title",role:"dialog","aria-modal":"true"},St={class:"flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0"},jt={class:"inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full"},qt={class:"bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4"},Ft={class:"sm:flex sm:items-start"},Lt={class:"mt-3 text-center sm:mt-0 sm:text-left w-full"},Pt={class:"mt-4"},Ut={class:"grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2"},$t={class:"sm:col-span-1"},At={class:"mt-1 text-sm text-gray-900"},Bt={class:"sm:col-span-1"},Qt={class:"mt-1 text-sm text-gray-900"},Tt={class:"sm:col-span-1"},Gt={class:"mt-1 text-sm text-gray-900"},Ot={class:"sm:col-span-2"},Wt={class:"mt-1 text-sm text-gray-900"},zt={class:"mt-6"},Ht={class:"mt-2 border border-gray-200 rounded-md overflow-hidden"},Jt={class:"divide-y divide-gray-200"},Kt={class:"grid grid-cols-5 gap-2 items-center"},Xt={class:"col-span-2 text-sm font-medium text-gray-900"},Yt={class:"col-span-1 text-center text-sm text-gray-500"},Zt={class:"col-span-1 text-center text-sm text-green-600 font-medium"},te={class:"col-span-1 text-center text-sm font-medium text-gray-900"},ee={class:"bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse"},ae={__name:"Restocks",setup(se){const w=Q(),M=f([]),S=f([]),g=f([]),N=f(!0),h=f(null),b=f(!1),E=f(!1),C=f(!1),x=f(null),_=f(""),p=f({id:null,visit_date:"",notes:"",location:"",machines:[]}),j=o=>o?new Date(o).toLocaleString():"",q=async()=>{N.value=!0;try{const o=await v.getVisits();M.value=o.data.map(e=>({id:e.id,location_id:e.location,location_name:e.location_name,visit_date:e.visit_date,notes:e.notes,user_name:e.user_name}))}catch(o){console.error("Error fetching visits:",o),h.value="Failed to load visits. Please try again later."}finally{N.value=!1}},P=async()=>{try{const o=await v.getLocations();S.value=o.data}catch(o){console.error("Error fetching locations:",o)}},F=async()=>{if(!_.value){g.value=[];return}try{const e=(await v.getMachines({location:_.value})).data,c=[];for(const l of e){const m=(await v.getMachineItems({machine:l.id})).data.map(u=>({id:u.product,name:u.product_name,price:u.price,current_stock:u.current_stock||0,stock_before:u.current_stock||0,restocked:0}));c.push({...l,products:m})}g.value=c}catch(o){console.error("Error fetching machines and products:",o),h.value="Failed to load machine products. Please try again."}},L=()=>{C.value=!1,x.value=null,_.value="",g.value=[],p.value={id:null,visit_date:new Date().toISOString().slice(0,16),notes:"",location:"",machines:[]},b.value=!0},U=async o=>{C.value=!0,x.value=o,_.value=o.location_id,p.value={id:o.id,visit_date:o.visit_date,notes:o.notes,location:o.location_id},await F();try{const c=(await v.getRestocks({visit:o.id})).data;for(const l of c){const m=(await v.getRestockEntries({visit_machine_restock:l.id})).data,u=g.value.findIndex(s=>s.id===l.machine);if(u!==-1){const s=g.value[u];m.forEach(r=>{const y=s.products.findIndex(B=>B.id===r.product);y!==-1&&(s.products[y].stock_before=r.stock_before,s.products[y].restocked=r.restocked)})}}b.value=!0}catch(e){console.error("Error loading visit for editing:",e),h.value="Failed to load visit details for editing. Please try again."}},$=async o=>{x.value=o;try{const c=(await v.getRestocks({visit:o.id})).data,l=[];for(const i of c){const m=await v.getRestockEntries({visit_machine_restock:i.id});l.push(...m.data)}x.value={...o,entries:l.map(i=>({id:i.id,product_name:i.product_name,product_id:i.product,previous_quantity:i.stock_before,quantity_added:i.restocked,machine_info:i.machine_info}))},E.value=!0}catch(e){console.error("Error fetching visit details:",e),h.value="Failed to load visit details. Please try again."}},A=async()=>{var o;try{if(g.value.some(i=>i.products.some(m=>m.stock_before===""||m.restocked===""))){h.value="Please record stock levels for all products in all machines";return}let c;const l={location:_.value,visit_date:p.value.visit_date,notes:p.value.notes,user:(o=w.user)==null?void 0:o.id};console.log("Saving visit with data:",l),C.value&&p.value.id?c=(await v.updateVisit(p.value.id,l)).data.id:c=(await v.createVisit(l)).data.id;for(const i of g.value){const m={visit:c,machine:i.id,notes:""},s=(await v.createRestock(m)).data.id;for(const r of i.products){const y={visit_machine_restock:s,product:r.id,stock_before:parseInt(r.stock_before)||0,restocked:parseInt(r.restocked)||0};await v.createRestockEntry(y)}}b.value=!1,await q()}catch(e){console.error("Error saving restock visit:",e),h.value="Failed to save visit. Please try again."}};return T(async()=>{w.isAuthenticated&&!w.user&&await w.fetchUser(),console.log("Current user:",w.user),await Promise.all([q(),P()])}),(o,e)=>{var c,l,i,m,u;return n(),a("div",null,[t("div",{class:"flex justify-between items-center mb-6"},[e[7]||(e[7]=t("h1",{class:"text-2xl font-semibold text-gray-900"},"Location Visits",-1)),t("button",{onClick:L,class:"inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"}," Record New Visit ")]),N.value?(n(),a("div",z,e[8]||(e[8]=[t("div",{class:"animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"},null,-1)]))):h.value?(n(),a("div",H,[t("div",J,[e[9]||(e[9]=t("div",{class:"flex-shrink-0"},[t("span",{class:"text-red-400"},"⚠")],-1)),t("div",K,[t("p",X,d(h.value),1)])])])):M.value.length===0?(n(),a("div",Y,[t("div",{class:"px-4 py-5 sm:p-6 text-center"},[e[10]||(e[10]=t("h3",{class:"text-lg leading-6 font-medium text-gray-900"},"No visits recorded",-1)),e[11]||(e[11]=t("div",{class:"mt-2 max-w-xl text-sm text-gray-500"},[t("p",null,"Get started by recording your first location visit.")],-1)),t("div",{class:"mt-5"},[t("button",{onClick:L,class:"inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"}," Record New Visit ")])])])):(n(),a("div",Z,[t("ul",tt,[(n(!0),a(k,null,R(M.value,s=>(n(),a("li",{key:s.id,class:"px-4 py-4 sm:px-6"},[t("div",et,[t("div",st,[t("p",ot,d(s.location_name),1),t("p",it,d(j(s.visit_date)),1)]),t("div",at,[t("button",{onClick:r=>$(s),class:"inline-flex items-center px-3 py-1 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"}," View Details ",8,nt),t("button",{onClick:r=>U(s),class:"inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"}," Edit ",8,rt)])])]))),128))])])),b.value?(n(),a("div",dt,[t("div",lt,[t("div",{class:"fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity","aria-hidden":"true",onClick:e[0]||(e[0]=s=>b.value=!1)}),e[20]||(e[20]=t("span",{class:"hidden sm:inline-block sm:align-middle sm:h-screen","aria-hidden":"true"},"​",-1)),t("div",ct,[t("form",{onSubmit:G(A,["prevent"])},[t("div",mt,[t("div",ut,[t("div",vt,[t("h3",ft,d(C.value?"Edit Visit":"Record New Visit"),1),t("div",pt,[t("div",null,[e[13]||(e[13]=t("label",{for:"location",class:"block text-sm font-medium text-gray-700"},"Location",-1)),V(t("select",{id:"location",name:"location","onUpdate:modelValue":e[1]||(e[1]=s=>_.value=s),onChange:F,class:"mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md",required:""},[e[12]||(e[12]=t("option",{value:"",disabled:""},"Select a location",-1)),(n(!0),a(k,null,R(S.value,s=>(n(),a("option",{key:s.id,value:s.id},d(s.name),9,gt))),128))],544),[[O,_.value]])]),t("div",null,[e[14]||(e[14]=t("label",{for:"visit_date",class:"block text-sm font-medium text-gray-700"},"Visit Date",-1)),V(t("input",{type:"datetime-local",name:"visit_date",id:"visit_date","onUpdate:modelValue":e[2]||(e[2]=s=>p.value.visit_date=s),class:"mt-1 focus:ring-primary-500 focus:border-primary-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md",required:""},null,512),[[I,p.value.visit_date]])]),g.value.length>0?(n(),a("div",xt,[e[17]||(e[17]=t("h4",{class:"text-sm font-medium text-gray-700 mb-2"},"Machines at Location",-1)),t("div",yt,[(n(!0),a(k,null,R(g.value,s=>(n(),a("div",{key:s.id,class:"border rounded-lg p-4"},[t("div",ht,[t("h5",_t,d(s.machine_type)+" ("+d(s.model)+") ",1),t("div",bt,d(s.products.length)+" products ",1)]),t("div",wt,[s.products.length===0?(n(),a("div",kt," No products in this machine ")):D("",!0),(n(!0),a(k,null,R(s.products,r=>(n(),a("div",{key:r.id,class:"grid grid-cols-4 gap-4 items-center"},[t("div",Rt,d(r.name),1),t("div",Vt,[e[15]||(e[15]=t("label",{class:"block text-xs text-gray-500"},"Current Stock",-1)),V(t("input",{type:"number","onUpdate:modelValue":y=>r.stock_before=y,min:"0",class:"mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm",required:""},null,8,Et),[[I,r.stock_before]])]),t("div",Ct,[e[16]||(e[16]=t("label",{class:"block text-xs text-gray-500"},"Restock Amount",-1)),V(t("input",{type:"number","onUpdate:modelValue":y=>r.restocked=y,min:"0",class:"mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm",required:""},null,8,Dt),[[I,r.restocked]])]),t("div",It," New Total: "+d((parseInt(r.stock_before)||0)+(parseInt(r.restocked)||0)),1)]))),128))])]))),128))])])):D("",!0),t("div",null,[e[18]||(e[18]=t("label",{for:"notes",class:"block text-sm font-medium text-gray-700"},"Visit Notes",-1)),V(t("textarea",{id:"notes",name:"notes",rows:"2","onUpdate:modelValue":e[3]||(e[3]=s=>p.value.notes=s),class:"shadow-sm focus:ring-primary-500 focus:border-primary-500 mt-1 block w-full sm:text-sm border border-gray-300 rounded-md"},null,512),[[I,p.value.notes]])])])])])]),t("div",Mt,[e[19]||(e[19]=t("button",{type:"submit",class:"w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-primary-600 text-base font-medium text-white hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 sm:ml-3 sm:w-auto sm:text-sm"}," Save Visit ",-1)),t("button",{type:"button",onClick:e[4]||(e[4]=s=>b.value=!1),class:"mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"}," Cancel ")])],32)])])])):D("",!0),E.value?(n(),a("div",Nt,[t("div",St,[t("div",{class:"fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity","aria-hidden":"true",onClick:e[5]||(e[5]=s=>E.value=!1)}),e[28]||(e[28]=t("span",{class:"hidden sm:inline-block sm:align-middle sm:h-screen","aria-hidden":"true"},"​",-1)),t("div",jt,[t("div",qt,[t("div",Ft,[t("div",Lt,[e[27]||(e[27]=t("h3",{class:"text-lg leading-6 font-medium text-gray-900",id:"modal-title"}," Restock Details ",-1)),t("div",Pt,[t("dl",Ut,[t("div",$t,[e[21]||(e[21]=t("dt",{class:"text-sm font-medium text-gray-500"},"Location",-1)),t("dd",At,d((c=x.value)==null?void 0:c.location_name),1)]),t("div",Bt,[e[22]||(e[22]=t("dt",{class:"text-sm font-medium text-gray-500"},"Visit Date",-1)),t("dd",Qt,d(j((l=x.value)==null?void 0:l.visit_date)),1)]),t("div",Tt,[e[23]||(e[23]=t("dt",{class:"text-sm font-medium text-gray-500"},"Restocked By",-1)),t("dd",Gt,d((i=x.value)==null?void 0:i.user_name),1)]),t("div",Ot,[e[24]||(e[24]=t("dt",{class:"text-sm font-medium text-gray-500"},"Notes",-1)),t("dd",Wt,d(((m=x.value)==null?void 0:m.notes)||"No notes"),1)])]),t("div",zt,[e[26]||(e[26]=t("h4",{class:"text-sm font-medium text-gray-500"},"Restocked Items",-1)),t("div",Ht,[e[25]||(e[25]=W('<div class="px-4 py-3 bg-gray-50 text-xs font-medium text-gray-500 uppercase tracking-wider"><div class="grid grid-cols-5 gap-2"><div class="col-span-2">Product</div><div class="col-span-1 text-center">Prev Qty</div><div class="col-span-1 text-center">Added</div><div class="col-span-1 text-center">New Qty</div></div></div>',1)),t("div",Jt,[(n(!0),a(k,null,R((u=x.value)==null?void 0:u.entries,s=>(n(),a("div",{key:s.id,class:"px-4 py-3"},[t("div",Kt,[t("div",Xt,d(s.product_name),1),t("div",Yt,d(s.previous_quantity),1),t("div",Zt," +"+d(s.quantity_added),1),t("div",te,d(s.previous_quantity+s.quantity_added),1)])]))),128))])])])])])])]),t("div",ee,[t("button",{type:"button",onClick:e[6]||(e[6]=s=>E.value=!1),class:"w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 sm:w-auto sm:text-sm"}," Close ")])])])])):D("",!0)])}}};export{ae as default};
