import{m as y,r as a,c as d,a as e,e as x,t as u,f as c,v as m,w,k as h,p as _,q as k,s as S,x as V,d as p,g as N}from"./index-D9zG8uyo.js";const C={key:0,class:"bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4",role:"alert"},L={class:"block sm:inline"},j={class:"mt-1"},q={class:"mt-1"},B=["disabled"],D={class:"mt-6"},U={class:"mt-6"},T={__name:"Login",setup(A){const f=V(),v=y(),n=a(""),l=a(""),o=a(!1),r=a(""),g=async()=>{r.value="",o.value=!0;try{const t=await v.login(n.value,l.value);t.success?f.push("/"):r.value=t.message||"Login failed"}catch(t){r.value="An error occurred during login",console.error("Login error:",t)}finally{o.value=!1}};return(t,s)=>{const b=S("router-link");return p(),d("div",null,[s[6]||(s[6]=e("h2",{class:"text-2xl font-semibold text-center mb-6"},"Sign In",-1)),r.value?(p(),d("div",C,[e("span",L,u(r.value),1)])):x("",!0),e("form",{onSubmit:w(g,["prevent"]),class:"space-y-6"},[e("div",null,[s[2]||(s[2]=e("label",{for:"username",class:"block text-sm font-medium text-gray-700"},"Username",-1)),e("div",j,[c(e("input",{id:"username","onUpdate:modelValue":s[0]||(s[0]=i=>n.value=i),name:"username",type:"text",required:"",class:"appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm"},null,512),[[m,n.value]])])]),e("div",null,[s[3]||(s[3]=e("label",{for:"password",class:"block text-sm font-medium text-gray-700"},"Password",-1)),e("div",q,[c(e("input",{id:"password","onUpdate:modelValue":s[1]||(s[1]=i=>l.value=i),name:"password",type:"password",required:"",class:"appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm"},null,512),[[m,l.value]])])]),e("div",null,[e("button",{type:"submit",disabled:o.value,class:"w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"},u(o.value?"Signing in...":"Sign in"),9,B)])],32),e("div",D,[s[5]||(s[5]=h('<div class="relative"><div class="absolute inset-0 flex items-center"><div class="w-full border-t border-gray-300"></div></div><div class="relative flex justify-center text-sm"><span class="px-2 bg-white text-gray-500">Don&#39;t have an account?</span></div></div>',1)),e("div",U,[_(b,{to:"/register",class:"w-full flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"},{default:k(()=>s[4]||(s[4]=[N(" Create a new account ")])),_:1})])])])}}};export{T as default};
