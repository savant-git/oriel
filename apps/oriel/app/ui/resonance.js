import * as THREE from "three";
import * as Tone from "tone";

const canvas = document.getElementById("scene");
const renderer = new THREE.WebGLRenderer({canvas, antialias:true});
renderer.setSize(window.innerWidth, window.innerHeight);
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(60, window.innerWidth/window.innerHeight, 0.1, 1000);
camera.position.z = 5;

// simple geometry pool for “shards”
const shards = [];
const material = new THREE.MeshStandardMaterial({color:0x66ccff, emissive:0x113355});
for(let i=0;i<20;i++){
  const m = new THREE.Mesh(new THREE.SphereGeometry(0.15), material.clone());
  m.position.set(Math.random()*4-2,Math.random()*3-1.5,Math.random()*3-1.5);
  scene.add(m);
  shards.push(m);
}

// lighting
const light = new THREE.PointLight(0xffffff,1.2);
light.position.set(2,2,5);
scene.add(light);
scene.add(new THREE.AmbientLight(0x404040));

// tone.js setup
const synth = new Tone.PolySynth(Tone.Synth).toDestination();
Tone.start();

// animation loop
function animate() {
  requestAnimationFrame(animate);
  shards.forEach((s,i)=>{
    s.rotation.x += 0.002 + Math.sin(Date.now()/1000+i)*0.001;
    s.rotation.y += 0.003;
  });
  renderer.render(scene, camera);
}
animate();

// receive Oriel events from main process
window.OrielAPI.onLog(text=>{
  const match = text.match(/Payloads:\s*(\d+)/);
  if(match){
    const val = parseInt(match[1]);
    const freq = 100 + val*5;
    synth.triggerAttackRelease(freq,"8n");
    shards[val % shards.length].material.emissive.setHex(0x22ff44);
  }
});
