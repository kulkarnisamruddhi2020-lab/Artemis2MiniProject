const canvas = document.getElementById('trajectoryMap');
const ctx = canvas.getContext('2d');

let graphData = { nodes: {}, edges: [] };
let currentNode = null;
let abortPath = null;
let simTime = 0.0;

// UI Elements
const btnStart = document.getElementById('btnStart');
const btnStep = document.getElementById('btnStep');
const btnAbort = document.getElementById('btnAbort');
const clockEl = document.getElementById('clock');

// Load Graph Config
async function initGraph() {
    const res = await fetch('/api/graph/config');
    graphData = await res.json();
    drawGraph();
}

function drawGraph() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Draw edges
    ctx.lineWidth = 1.5;
    graphData.edges.forEach(edge => {
        const s = graphData.nodes[edge.source];
        const t = graphData.nodes[edge.target];
        if(!s || !t) return;
        
        // Is it part of the abort path?
        let isAbort = false;
        if (abortPath) {
            for(let i=0; i<abortPath.length-1; i++){
                if((abortPath[i] === edge.source && abortPath[i+1] === edge.target)) isAbort = true;
            }
        }

        ctx.strokeStyle = isAbort ? '#ff003c' : 'rgba(102, 252, 241, 0.2)';
        ctx.setLineDash(isAbort ? [5, 5] : []);
        ctx.beginPath();
        ctx.moveTo(s.x, s.y);
        ctx.lineTo(t.x, t.y);
        ctx.stroke();
    });
    ctx.setLineDash([]);

    // Draw nodes
    Object.entries(graphData.nodes).forEach(([id, node]) => {
        ctx.beginPath();
        ctx.arc(node.x, node.y, 8, 0, Math.PI * 2);
        ctx.fillStyle = (id === currentNode) ? '#fff' : '#1f2833';
        ctx.fill();
        ctx.strokeStyle = (id === currentNode) ? '#66fcf1' : '#45a29e';
        ctx.lineWidth = 2;
        ctx.stroke();

        ctx.fillStyle = '#c5c6c7';
        ctx.font = '12px "Share Tech Mono"';
        ctx.fillText(node.label, node.x + 15, node.y + 4);
    });

    // Draw Ship
    if (currentNode && graphData.nodes[currentNode]) {
        drawShip(graphData.nodes[currentNode]);
    }
}

function drawShip(node) {
    ctx.beginPath();
    ctx.arc(node.x, node.y, 14, 0, Math.PI * 2);
    ctx.strokeStyle = '#ff003c';
    ctx.lineWidth = 2;
    ctx.stroke();
    // Pulse effect
    ctx.beginPath();
    ctx.arc(node.x, node.y, 22, 0, Math.PI * 2);
    ctx.strokeStyle = 'rgba(255, 0, 60, 0.5)';
    ctx.stroke();
}

function updateTelemetry(data) {
    document.getElementById('t-stage').innerText = data.node;
    document.getElementById('t-alt').innerText = data.telemetry.alt.toFixed(2);
    document.getElementById('t-vel').innerText = data.telemetry.vel.toFixed(2);
    document.getElementById('t-status').innerText = data.status.toUpperCase();
    
    if(data.status === 'aborted') {
        document.getElementById('t-status').style.color = 'var(--danger)';
    } else {
        document.getElementById('t-status').style.color = 'var(--accent)';
    }
}

btnStart.addEventListener('click', async () => {
    await fetch('/api/simulation/reset', { method: 'POST' });
    btnStep.disabled = false;
    btnAbort.disabled = false;
    currentNode = "Pad_39B";
    abortPath = null;
    simTime = 0;
    targetVisualTime = 0;
    visualTime = 0;
    isVisualAbort = false;
    activeVisualNodes = ["Pad_39B", "LEO", "HEO", "TLI", "Lunar_Flyby", "Earth_Orbit", "Splashdown"];
    
    clockEl.innerText = "00:00:00";
    document.getElementById('t-stage').innerText = 'INITIALIZED';
    document.getElementById('visualizerStatus').innerText = 'Ship Integrity: NOMINAL';
    document.getElementById('visualizerStatus').style.color = '#45a29e';
    drawGraph();
});

btnStep.addEventListener('click', async () => {
    const res = await fetch('/api/simulation/step', { method: 'POST' });
    const data = await res.json();
    
    if (data.status === 'finished') {
        btnStep.disabled = true;
        btnAbort.disabled = true;
        document.getElementById('t-status').innerText = 'MISSION COMPLETE';
        return;
    }
    
    const state = data.state;
    currentNode = state.node;
    simTime = state.timestamp;
    targetVisualTime = simTime; // Let visualizer catch up
    
    // Format clock
    let hrs = Math.floor(simTime);
    let mins = Math.floor((simTime - hrs) * 60);
    clockEl.innerText = `${hrs.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}:00`;
    
    updateTelemetry(state);
    drawGraph();
});

btnAbort.addEventListener('click', async () => {
    if (!currentNode) return;
    
    // Play Siren Alarm
    try {
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioCtx.createOscillator();
        const gainNode = audioCtx.createGain();
        oscillator.connect(gainNode);
        gainNode.connect(audioCtx.destination);
        oscillator.type = 'square';
        oscillator.frequency.value = 800;
        
        gainNode.gain.setValueAtTime(0, audioCtx.currentTime);
        for(let j=0; j<10; j++) {
            gainNode.gain.linearRampToValueAtTime(0.3, audioCtx.currentTime + j*0.5 + 0.1);
            gainNode.gain.linearRampToValueAtTime(0, audioCtx.currentTime + j*0.5 + 0.4);
        }
        oscillator.start();
        oscillator.stop(audioCtx.currentTime + 5);
    } catch(e) {}
    
    const res = await fetch('/api/simulation/abort', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ current_node: currentNode })
    });
    
    const data = await res.json();
    if (data.status === 'success') {
        abortPath = data.abort_info.path;
        
        // Push abort path to visualizer
        isVisualAbort = true;
        let pth = [];
        let hit = false;
        for (let n of ["Pad_39B", "LEO", "HEO", "TLI", "Lunar_Flyby", "Earth_Orbit", "Splashdown"]) {
            pth.push(n);
            if (n === currentNode) break;
        }
        for (let i = 1; i < abortPath.length; i++) {
            pth.push(abortPath[i]);
        }
        activeVisualNodes = pth;

        btnAbort.disabled = true; // Can only abort once
        document.getElementById('t-status').innerText = 'ABORT INITIATED';
        document.getElementById('t-status').style.color = 'var(--danger)';
        document.getElementById('visualizerStatus').innerText = 'CRITICAL: EMERGENCY OFF-NOMINAL TRAJECTORY ENABLED';
        document.getElementById('visualizerStatus').style.color = '#ff003c';
        document.getElementById('visualizerStatus').style.animation = 'pulse 1s infinite';
        drawGraph();
    }
});

// ======= NASA EXACT ORBITAL VISUALIZER =======
const miniCanvas = document.getElementById('miniSimCanvas');
const mCtx = miniCanvas.getContext('2d');

let visualTime = 0;
let targetVisualTime = 0;

// Hardcoded coordinates that visually mimic the NASA Artemis 2 Free-Return Trajectory
const miniNodes = {
    Pad_39B: {x: 75, y: 80},
    LEO: {x: 55, y: 55},
    HEO: {x: 40, y: 110},
    TLI: {x: 120, y: 55},       // Start of transfer
    Lunar_Flyby: {x: 245, y: 80}, // Far side of the Moon
    Earth_Orbit: {x: 120, y: 110}, // Coming back under Earth
    Splashdown: {x: 75, y: 80}
};

const orbitCurves = {
    "Pad_39B-LEO": [{x: 65, y: 65}],
    "LEO-HEO": [{x: 35, y: 40}, {x: 20, y: 100}],
    "HEO-TLI": [{x: 60, y: 130}, {x: 100, y: 80}],
    "TLI-Lunar_Flyby": [{x: 160, y: 30}, {x: 235, y: 30}],
    "Lunar_Flyby-Earth_Orbit": [{x: 240, y: 130}, {x: 160, y: 130}],
    "Earth_Orbit-Splashdown": [{x: 100, y: 90}],
    // Emergency Route Curves
    "LEO-Splashdown": [{x: 60, y: 60}],
    "HEO-Splashdown": [{x: 30, y: 140}, {x: 60, y: 100}],
    "TLI-Earth_Orbit": [{x: 120, y: 80}],
    "TLI-Splashdown": [{x: 100, y: 60}],
    "Lunar_Flyby-Splashdown": [{x: 180, y: 130}, {x: 100, y: 100}]
};

let activeVisualNodes = ["Pad_39B", "LEO", "HEO", "TLI", "Lunar_Flyby", "Earth_Orbit", "Splashdown"];
let isVisualAbort = false;

function drawVisualizer() {
    mCtx.clearRect(0, 0, miniCanvas.width, miniCanvas.height);
    
    // Draw tiny Earth
    mCtx.beginPath(); mCtx.arc(75, 80, 18, 0, Math.PI * 2);
    mCtx.fillStyle = '#0a2a4b'; mCtx.fill();
    mCtx.lineWidth = 1; mCtx.strokeStyle = '#1d5e9b'; mCtx.stroke();
    
    // Draw tiny Moon
    mCtx.beginPath(); mCtx.arc(225, 80, 10, 0, Math.PI * 2);
    mCtx.fillStyle = '#333'; mCtx.fill();
    mCtx.strokeStyle = '#555'; mCtx.stroke();
    
    // Draw Active Mission Path
    mCtx.beginPath();
    let startNode = miniNodes[activeVisualNodes[0]] || miniNodes['Pad_39B'];
    mCtx.moveTo(startNode.x, startNode.y);

    for (let i = 1; i < activeVisualNodes.length; i++) {
        let prev = activeVisualNodes[i-1];
        let curr = activeVisualNodes[i];
        let p2 = miniNodes[curr] || miniNodes['Pad_39B'];
        let cps = orbitCurves[`${prev}-${curr}`];
        
        if (cps) {
            if (cps.length === 1) mCtx.quadraticCurveTo(cps[0].x, cps[0].y, p2.x, p2.y);
            else mCtx.bezierCurveTo(cps[0].x, cps[0].y, cps[1].x, cps[1].y, p2.x, p2.y);
        } else {
            mCtx.lineTo(p2.x, p2.y);
        }
    }
    
    mCtx.strokeStyle = isVisualAbort ? '#ff003c' : 'rgba(102, 252, 241, 0.3)';
    mCtx.setLineDash(isVisualAbort ? [4, 4] : []);
    mCtx.lineWidth = 1.5;
    mCtx.stroke();
    mCtx.setLineDash([]);
    
    visualTime += (targetVisualTime - visualTime) * 0.05;

    mCtx.beginPath();
    let anchor = miniNodes[currentNode] || miniNodes["Pad_39B"];
    mCtx.arc(anchor.x, anchor.y, 4, 0, Math.PI * 2);
    mCtx.fillStyle = '#ff003c';
    mCtx.fill();
    mCtx.shadowBlur = 10;
    mCtx.shadowColor = '#ff003c';
    mCtx.stroke(); mCtx.shadowBlur = 0;
    
    requestAnimationFrame(drawVisualizer);
}

drawVisualizer();

// Init on load
initGraph();
