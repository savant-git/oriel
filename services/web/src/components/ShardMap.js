import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";

export function initShardMap() {
  const canvas = document.getElementById("shard-map");
  if (!canvas) return;
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(50, 600/400, 0.1, 1000);
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
  renderer.setSize(600, 400);
  camera.position.z = 10;

  const material = new THREE.MeshStandardMaterial({ color: 0xe4c66f });
  for (let i = 0; i < 20; i++) {
    const sphere = new THREE.Mesh(new THREE.SphereGeometry(0.15, 16, 16), material);
    sphere.position.set(Math.random()*6-3, Math.random()*3-1.5, Math.random()*2-1);
    scene.add(sphere);
  }

  const light = new THREE.PointLight(0xffffff, 1);
  light.position.set(10,10,10);
  scene.add(light);

  const controls = new OrbitControls(camera, renderer.domElement);
  const animate = () => {
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
  };
  animate();
}
