import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";

export function initShardMap() {
  const canvas = document.getElementById("shard-map") as HTMLCanvasElement;
  if (!canvas) return;

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(45, canvas.width / canvas.height, 0.1, 100);
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
  renderer.setSize(canvas.width, canvas.height);

  const material = new THREE.MeshStandardMaterial({ color: 0xe4c66f });
  for (let i = 0; i < 25; i++) {
    const sphere = new THREE.Mesh(new THREE.SphereGeometry(0.12, 16, 16), material);
    sphere.position.set(Math.random() * 6 - 3, Math.random() * 3 - 1.5, Math.random() * 2 - 1);
    scene.add(sphere);
  }

  const light = new THREE.PointLight(0xffffff, 1);
  light.position.set(5, 5, 5);
  scene.add(light);

  const controls = new OrbitControls(camera, renderer.domElement);
  camera.position.z = 6;

  const animate = () => {
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
  };
  animate();
}
