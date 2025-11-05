"use client";
import { useEffect,useState } from "react";
import io from "socket.io-client";
import { motion } from "framer-motion";
const socket=io("http://127.0.0.1:5050");
export default function Soundboard(){
  const [name,setName]=useState("");const [paths,setPaths]=useState("");
  function save(){
    const p=paths.split("\\n").map(x=>x.trim()).filter(Boolean);
    fetch("http://127.0.0.1:5050/save",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({name,paths:p})});
    setName("");setPaths("");
  }
  useEffect(()=>{socket.on("status",m=>console.log(m));},[]);
  return(
  <motion.div initial={{opacity:0}} animate={{opacity:1}}>
    <h2 className="text-4xl font-mono mb-6 text-gold">soundboard</h2>
    <div className="flex gap-2 mb-4">
      <input value={name} onChange={e=>setName(e.target.value)} placeholder="group name"
        className="flex-1 bg-gunmetal-light px-3 py-2 rounded-md border border-gold-dark text-gold-light"/>
      <button onClick={save}>save</button>
    </div>
    <textarea value={paths} onChange={e=>setPaths(e.target.value)} placeholder="script paths (one per line)"
      className="w-full bg-gunmetal-light text-gold-light border border-gold-dark rounded-md p-3 h-40 mb-4"/>
  </motion.div>);
}
