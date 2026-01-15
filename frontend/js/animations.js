// Three.js 3D Background Animation

let scene, camera, renderer, particles;

function initThreeJS() {
    const canvas = document.getElementById('bg-canvas');

    // Scene setup
    scene = new THREE.Scene();

    // Camera setup
    camera = new THREE.PerspectiveCamera(
        75,
        window.innerWidth / window.innerHeight,
        0.1,
        1000
    );
    camera.position.z = 30;

    // Renderer setup
    renderer = new THREE.WebGLRenderer({
        canvas: canvas,
        alpha: true,
        antialias: true
    });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(window.devicePixelRatio);

    // Create particles
    createParticles();

    // Create geometric shapes
    createGeometricShapes();

    // Mouse interaction
    setupMouseInteraction();

    // Animation loop
    animate();

    // Handle resize
    window.addEventListener('resize', onWindowResize);
}

function createParticles() {
    const geometry = new THREE.BufferGeometry();
    const vertices = [];
    const colors = [];

    for (let i = 0; i < 1000; i++) {
        const x = (Math.random() - 0.5) * 100;
        const y = (Math.random() - 0.5) * 100;
        const z = (Math.random() - 0.5) * 100;

        vertices.push(x, y, z);

        // Color gradient
        const color = new THREE.Color();
        color.setHSL(Math.random() * 0.3 + 0.6, 0.8, 0.6);
        colors.push(color.r, color.g, color.b);
    }

    geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
    geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));

    const material = new THREE.PointsMaterial({
        size: 0.5,
        vertexColors: true,
        transparent: true,
        opacity: 0.8,
        blending: THREE.AdditiveBlending
    });

    particles = new THREE.Points(geometry, material);
    scene.add(particles);
}

function createGeometricShapes() {
    // Create floating geometric shapes
    const shapes = [];

    // Torus
    const torusGeometry = new THREE.TorusGeometry(5, 1, 16, 100);
    const torusMaterial = new THREE.MeshBasicMaterial({
        color: 0x6366f1,
        wireframe: true,
        transparent: true,
        opacity: 0.3
    });
    const torus = new THREE.Mesh(torusGeometry, torusMaterial);
    torus.position.set(-15, 10, -10);
    scene.add(torus);
    shapes.push(torus);

    // Icosahedron
    const icoGeometry = new THREE.IcosahedronGeometry(3, 0);
    const icoMaterial = new THREE.MeshBasicMaterial({
        color: 0xec4899,
        wireframe: true,
        transparent: true,
        opacity: 0.3
    });
    const icosahedron = new THREE.Mesh(icoGeometry, icoMaterial);
    icosahedron.position.set(15, -10, -15);
    scene.add(icosahedron);
    shapes.push(icosahedron);

    // Octahedron
    const octaGeometry = new THREE.OctahedronGeometry(4, 0);
    const octaMaterial = new THREE.MeshBasicMaterial({
        color: 0x14b8a6,
        wireframe: true,
        transparent: true,
        opacity: 0.3
    });
    const octahedron = new THREE.Mesh(octaGeometry, octaMaterial);
    octahedron.position.set(0, 15, -20);
    scene.add(octahedron);
    shapes.push(octahedron);

    // Store shapes for animation
    window.geometricShapes = shapes;
}

let mouseX = 0;
let mouseY = 0;

function setupMouseInteraction() {
    document.addEventListener('mousemove', (event) => {
        mouseX = (event.clientX / window.innerWidth) * 2 - 1;
        mouseY = -(event.clientY / window.innerHeight) * 2 + 1;
    });
}

function animate() {
    requestAnimationFrame(animate);

    // Rotate particles
    if (particles) {
        particles.rotation.x += 0.0005;
        particles.rotation.y += 0.001;
    }

    // Animate geometric shapes
    if (window.geometricShapes) {
        window.geometricShapes.forEach((shape, index) => {
            shape.rotation.x += 0.01 * (index + 1);
            shape.rotation.y += 0.01 * (index + 1);

            // Mouse interaction
            shape.position.x += (mouseX * 5 - shape.position.x) * 0.01;
            shape.position.y += (mouseY * 5 - shape.position.y) * 0.01;
        });
    }

    // Camera movement based on mouse
    camera.position.x += (mouseX * 2 - camera.position.x) * 0.02;
    camera.position.y += (mouseY * 2 - camera.position.y) * 0.02;
    camera.lookAt(scene.position);

    renderer.render(scene, camera);
}

function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}

// Particles.js Configuration
function initParticlesJS() {
    if (typeof particlesJS !== 'undefined') {
        particlesJS('particles-js', {
            particles: {
                number: {
                    value: 80,
                    density: {
                        enable: true,
                        value_area: 800
                    }
                },
                color: {
                    value: ['#6366f1', '#ec4899', '#14b8a6']
                },
                shape: {
                    type: 'circle'
                },
                opacity: {
                    value: 0.5,
                    random: true,
                    anim: {
                        enable: true,
                        speed: 1,
                        opacity_min: 0.1,
                        sync: false
                    }
                },
                size: {
                    value: 3,
                    random: true,
                    anim: {
                        enable: true,
                        speed: 2,
                        size_min: 0.1,
                        sync: false
                    }
                },
                line_linked: {
                    enable: true,
                    distance: 150,
                    color: '#6366f1',
                    opacity: 0.2,
                    width: 1
                },
                move: {
                    enable: true,
                    speed: 1,
                    direction: 'none',
                    random: true,
                    straight: false,
                    out_mode: 'out',
                    bounce: false
                }
            },
            interactivity: {
                detect_on: 'canvas',
                events: {
                    onhover: {
                        enable: true,
                        mode: 'grab'
                    },
                    onclick: {
                        enable: true,
                        mode: 'push'
                    },
                    resize: true
                },
                modes: {
                    grab: {
                        distance: 140,
                        line_linked: {
                            opacity: 0.5
                        }
                    },
                    push: {
                        particles_nb: 4
                    }
                }
            },
            retina_detect: true
        });
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    if (typeof THREE !== 'undefined') {
        initThreeJS();
    }
    initParticlesJS();
});
