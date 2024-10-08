"use strict";(self.webpackChunkcode_confluence=self.webpackChunkcode_confluence||[]).push([[587],{5123:(e,a,s)=>{s.r(a),s.d(a,{default:()=>m});var l=s(6540),i=s(2130),t=s(3914),o=s(7875);const n={socialLinksContainer:"socialLinksContainer_Am_Y",socialLink:"socialLink_ufr6",icon:"icon_JETh",discordLink:"discordLink_OESF",twitterLink:"twitterLink_H3HS",bookCallLink:"bookCallLink_TVDS",callIcon:"callIcon_YpY3",detailsContainer:"detailsContainer_QKFp",locationContainer:"locationContainer_nl3g",locationIcon:"locationIcon_LDB4",locationInfo:"locationInfo_CSSw",locationTitle:"locationTitle_f9Be",locationAddress:"locationAddress_jg52"};var r=s(6188),c=s(1815),d=s(4848);function m(){const[e,a]=(0,l.useState)({firstName:"",lastName:"",email:"",message:""}),[s,m]=(0,l.useState)({}),h=e=>{const{name:s,value:l}=e.target;a((e=>({...e,[s]:l})))};return(0,d.jsx)(i.A,{title:"Contact Us",children:(0,d.jsxs)("div",{style:{padding:"2rem",maxWidth:"1400px",margin:"0 auto",display:"flex",gap:"6rem"},children:[(0,d.jsx)("div",{style:{backgroundColor:"#ffffff",padding:"4rem",boxShadow:"0 4px 8px 0 rgba(0,0,0,0.2), 0 6px 20px 0 rgba(0,0,0,0.19)"},children:(0,d.jsxs)("div",{style:{flex:1},children:[(0,d.jsx)("h1",{style:{marginBottom:"1rem"},children:"Contact Us"}),(0,d.jsx)("p",{style:{marginBottom:"2rem"},children:"Please fill this form in a decent manner"}),(0,d.jsxs)("form",{onSubmit:async s=>{s.preventDefault(),(()=>{let a={};return/^[a-zA-Z\s]*$/.test(e.firstName)||(a.firstName="First name should not contain numbers"),/^[a-zA-Z\s]*$/.test(e.lastName)||(a.lastName="Last name should not contain numbers"),/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(e.email)||(a.email="Please enter a valid email address"),""===e.message.trim()&&(a.message="Message cannot be empty"),m(a),0===Object.keys(a).length})()?c.Ay.send("service_gp4ccmu","template_3m1nbg5",e,"pevo5K5mvmR54CoKy").then((e=>{console.log(e.text),alert("Message sent successfully!"),a({firstName:"",lastName:"",email:"",message:""})}),(e=>{console.log(e.text),alert("Failed to send message. Please try again.")})):console.log("Form has errors")},children:[(0,d.jsxs)("div",{style:{marginBottom:"1.5rem"},children:[(0,d.jsx)("label",{htmlFor:"fullName",style:{display:"block",marginBottom:"0.5rem",fontWeight:"bold"},children:"Full Name *"}),(0,d.jsxs)("div",{style:{display:"flex",gap:"1rem"},children:[(0,d.jsxs)("div",{style:{flex:1},children:[(0,d.jsx)("input",{type:"text",id:"firstName",name:"firstName",value:e.firstName,onChange:h,required:!0,placeholder:"First Name",style:{width:"100%",padding:"0.5rem",border:"1px solid #ccc",borderRadius:"4px"}}),s.firstName&&(0,d.jsx)("div",{style:{color:"red",fontSize:"0.8rem"},children:s.firstName})]}),(0,d.jsxs)("div",{style:{flex:1},children:[(0,d.jsx)("input",{type:"text",id:"lastName",name:"lastName",value:e.lastName,onChange:h,required:!0,placeholder:"Last Name",style:{width:"100%",padding:"0.5rem",border:"1px solid #ccc",borderRadius:"4px"}}),s.lastName&&(0,d.jsx)("div",{style:{color:"red",fontSize:"0.8rem"},children:s.lastName})]})]})]}),(0,d.jsxs)("div",{style:{marginBottom:"1.5rem"},children:[(0,d.jsx)("label",{htmlFor:"email",style:{display:"block",marginBottom:"0.5rem",fontWeight:"bold"},children:"E-mail *"}),(0,d.jsx)("input",{type:"email",id:"email",name:"email",value:e.email,onChange:h,required:!0,placeholder:"example@example.com",style:{width:"100%",padding:"0.5rem",border:"1px solid #ccc",borderRadius:"4px"}}),s.email&&(0,d.jsx)("div",{style:{color:"red",fontSize:"0.8rem"},children:s.email})]}),(0,d.jsxs)("div",{style:{marginBottom:"1.5rem"},children:[(0,d.jsx)("label",{htmlFor:"message",style:{display:"block",marginBottom:"0.5rem",fontWeight:"bold"},children:"Message *"}),(0,d.jsx)("textarea",{id:"message",name:"message",value:e.message,onChange:h,required:!0,style:{width:"100%",padding:"0.5rem",border:"1px solid #ccc",borderRadius:"4px",minHeight:"150px"}}),s.message&&(0,d.jsx)("div",{style:{color:"red",fontSize:"0.8rem"},children:s.message})]}),(0,d.jsx)("button",{type:"submit",style:{padding:"0.75rem 2rem",backgroundColor:"#000",color:"white",border:"none",borderRadius:"4px",cursor:"pointer",fontSize:"1rem",fontWeight:"bold"},children:"SUBMIT"})]})]})}),(0,d.jsxs)("div",{style:{flex:1},children:[(0,d.jsxs)("div",{className:n.locationContainer,children:[(0,d.jsx)(t.g,{icon:r.Pcr,className:n.locationIcon}),(0,d.jsxs)("div",{className:n.locationInfo,children:[(0,d.jsx)("h3",{className:n.locationTitle,children:"Location"}),(0,d.jsx)("a",{href:"https://www.google.com/maps/search/?api=1&query=Gf-10+Allen+Complex,+Nizampura+Rd,+Nizampura+Char+Rasta,+LG+Nagar-390002,+Vadodara,+Gujarat",target:"_blank",rel:"noopener noreferrer",className:n.mapLink,children:(0,d.jsxs)("p",{className:n.locationAddress,children:["Gf-10 Allen Complex,",(0,d.jsx)("br",{}),"Nizampura Rd, Nizampura Char Rasta,",(0,d.jsx)("br",{}),"LG Nagar-390002, Vadodara, Gujarat"]})})]})]}),(0,d.jsx)("div",{className:n.bookCallContainer,children:(0,d.jsxs)("a",{href:"https://cal.com/jay-ghiya/15min",className:n.bookCallLink,children:[(0,d.jsx)(t.g,{icon:r.KKr,className:n.callIcon}),(0,d.jsx)("span",{children:"Book a Call"})]})}),(0,d.jsxs)("div",{className:n.socialLinksContainer,children:[(0,d.jsx)("a",{href:"https://discord.com/channels/1131597983058755675/1169968780953260106",className:`${n.socialLink} ${n.discordLink}`,children:(0,d.jsx)(t.g,{icon:o._2G,className:n.icon})}),(0,d.jsx)("a",{href:"https://x.com/unoplatio",className:`${n.socialLink} ${n.twitterLink}`,children:(0,d.jsx)(t.g,{icon:o.HQ1,className:n.icon})})]})]})]})})}}}]);