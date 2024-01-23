"use strict";(self.webpackChunkdocs=self.webpackChunkdocs||[]).push([[863],{394:(e,t,a)=>{a.r(t),a.d(t,{assets:()=>r,contentTitle:()=>o,default:()=>u,frontMatter:()=>i,metadata:()=>l,toc:()=>c});var n=a(5893),s=a(1151);const i={sidebar_position:4,hide_table_of_contents:!0},o="Evaluation",l={id:"guides/core-types/evaluations",title:"Evaluation",description:"Evaluation-driven development helps you reliably iterate on an application. The Evaluation class is designed to assess the performance of a Model on a given Dataset using specified scoring functions.",source:"@site/docs/guides/core-types/evaluations.md",sourceDirName:"guides/core-types",slug:"/guides/core-types/evaluations",permalink:"/weave/guides/core-types/evaluations",draft:!1,unlisted:!1,editUrl:"https://github.com/wandb/weave/blob/master/docs/docs/guides/core-types/evaluations.md",tags:[],version:"current",sidebarPosition:4,frontMatter:{sidebar_position:4,hide_table_of_contents:!0},sidebar:"documentationSidebar",previous:{title:"Datasets",permalink:"/weave/guides/core-types/datasets"},next:{title:"Tracking",permalink:"/weave/guides/tracking/"}},r={},c=[{value:"Create an Evaluation",id:"create-an-evaluation",level:2},{value:"Define an evaluation dataset",id:"define-an-evaluation-dataset",level:3}];function d(e){const t={a:"a",code:"code",h1:"h1",h2:"h2",h3:"h3",p:"p",pre:"pre",...(0,s.a)(),...e.components};return(0,n.jsxs)(n.Fragment,{children:[(0,n.jsx)(t.h1,{id:"evaluation",children:"Evaluation"}),"\n",(0,n.jsxs)(t.p,{children:["Evaluation-driven development helps you reliably iterate on an application. The ",(0,n.jsx)(t.code,{children:"Evaluation"})," class is designed to assess the performance of a ",(0,n.jsx)(t.code,{children:"Model"})," on a given ",(0,n.jsx)(t.code,{children:"Dataset"})," using specified scoring functions."]}),"\n",(0,n.jsx)(t.pre,{children:(0,n.jsx)(t.code,{className:"language-python",children:"from weave.weaveflow import Evaluation\n\nevaluation = Evaluation(\n    dataset, scores=[score], example_to_model_input=example_to_model_input\n)\nevaluation.evaluate(model)\n"})}),"\n",(0,n.jsx)(t.h2,{id:"create-an-evaluation",children:"Create an Evaluation"}),"\n",(0,n.jsxs)(t.p,{children:["To systematically improve your application, it's very helpful to test your changes against a consistent dataset of potential inputs so that you catch regressions. Using the ",(0,n.jsx)(t.code,{children:"Evaluation"})," class, you can be sure you're comparing apples-to-apples by keeping track of the model and dataset versions used."]}),"\n",(0,n.jsx)(t.h3,{id:"define-an-evaluation-dataset",children:"Define an evaluation dataset"}),"\n",(0,n.jsxs)(t.p,{children:["First, define a ",(0,n.jsx)(t.a,{href:"/guides/core-types/datasets",children:"Dataset"})," with a collection of examples to be evaluated. These examples are often failure cases that you want to test for, these are similar to unit tests in Test-Driven Development (TDD)."]}),"\n",(0,n.jsxs)(t.p,{children:["Then, define a list of scoring functions. Each function should take an example and a prediction, returning a dictionary with the scores. ",(0,n.jsx)(t.code,{children:"example_to_model_input"})," is a function that formats each example into a format that the model can process."]}),"\n",(0,n.jsxs)(t.p,{children:["Finally, create a model and pass this to ",(0,n.jsx)(t.code,{children:"evaluation.evaluate"}),", which will run ",(0,n.jsx)(t.code,{children:"predict"})," on each example and score the output with each scoring function."]}),"\n",(0,n.jsxs)(t.p,{children:["To see this in action, follow the '",(0,n.jsx)(t.a,{href:"/tutorial-eval",children:"Build an Evaluation pipeline"}),"' tutorial."]})]})}function u(e={}){const{wrapper:t}={...(0,s.a)(),...e.components};return t?(0,n.jsx)(t,{...e,children:(0,n.jsx)(d,{...e})}):d(e)}},1151:(e,t,a)=>{a.d(t,{Z:()=>l,a:()=>o});var n=a(7294);const s={},i=n.createContext(s);function o(e){const t=n.useContext(i);return n.useMemo((function(){return"function"==typeof e?e(t):{...t,...e}}),[t,e])}function l(e){let t;return t=e.disableParentContext?"function"==typeof e.components?e.components(s):e.components||s:o(e.components),n.createElement(i.Provider,{value:t},e.children)}}}]);