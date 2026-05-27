function initShapeGrid(canvas, options = {}) {
  const {
    direction = 'diagonal',
    speed = 0.5,
    borderColor = '#c5e8e5',
    squareSize = 40,
    hoverFillColor = '#7ECEC4',
    shape = 'square',
    hoverTrailAmount = 5,
  } = options;

  const ctx = canvas.getContext('2d');
  let animId;
  const gridOffset = { x: 0, y: 0 };
  let hoveredSquare = null;
  const trailCells = [];
  const cellOpacities = new Map();

  function resize() {
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;
  }

  window.addEventListener('resize', resize);
  resize();

  function drawGrid() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const offsetX = ((gridOffset.x % squareSize) + squareSize) % squareSize;
    const offsetY = ((gridOffset.y % squareSize) + squareSize) % squareSize;
    const cols = Math.ceil(canvas.width / squareSize) + 3;
    const rows = Math.ceil(canvas.height / squareSize) + 3;

    for (let col = -2; col < cols; col++) {
      for (let row = -2; row < rows; row++) {
        const sx = col * squareSize + offsetX;
        const sy = row * squareSize + offsetY;
        const key = `${col},${row}`;
        const alpha = cellOpacities.get(key);
        if (alpha) {
          ctx.globalAlpha = alpha;
          ctx.fillStyle = hoverFillColor;
          ctx.fillRect(sx, sy, squareSize, squareSize);
          ctx.globalAlpha = 1;
        }
        ctx.strokeStyle = borderColor;
        ctx.strokeRect(sx, sy, squareSize, squareSize);
      }
    }
  }

  function updateOpacities() {
    const targets = new Map();
    if (hoveredSquare) targets.set(`${hoveredSquare.x},${hoveredSquare.y}`, 1);
    if (hoverTrailAmount > 0) {
      trailCells.forEach((t, i) => {
        const key = `${t.x},${t.y}`;
        if (!targets.has(key)) targets.set(key, (trailCells.length - i) / (trailCells.length + 1));
      });
    }
    for (const [key] of targets) {
      if (!cellOpacities.has(key)) cellOpacities.set(key, 0);
    }
    for (const [key, opacity] of cellOpacities) {
      const target = targets.get(key) || 0;
      const next = opacity + (target - opacity) * 0.15;
      if (next < 0.005) cellOpacities.delete(key);
      else cellOpacities.set(key, next);
    }
  }

  function animate() {
    const wrap = squareSize;
    if (direction === 'right') gridOffset.x = (gridOffset.x - speed + wrap) % wrap;
    else if (direction === 'left') gridOffset.x = (gridOffset.x + speed + wrap) % wrap;
    else if (direction === 'up') gridOffset.y = (gridOffset.y + speed + wrap) % wrap;
    else if (direction === 'down') gridOffset.y = (gridOffset.y - speed + wrap) % wrap;
    else if (direction === 'diagonal') {
      gridOffset.x = (gridOffset.x - speed + wrap) % wrap;
      gridOffset.y = (gridOffset.y - speed + wrap) % wrap;
    }
    updateOpacities();
    drawGrid();
    animId = requestAnimationFrame(animate);
  }

  canvas.addEventListener('mousemove', e => {
    const rect = canvas.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;
    const offsetX = ((gridOffset.x % squareSize) + squareSize) % squareSize;
    const offsetY = ((gridOffset.y % squareSize) + squareSize) % squareSize;
    const col = Math.floor((mx - offsetX) / squareSize);
    const row = Math.floor((my - offsetY) / squareSize);
    if (!hoveredSquare || hoveredSquare.x !== col || hoveredSquare.y !== row) {
      if (hoveredSquare && hoverTrailAmount > 0) {
        trailCells.unshift({ ...hoveredSquare });
        if (trailCells.length > hoverTrailAmount) trailCells.length = hoverTrailAmount;
      }
      hoveredSquare = { x: col, y: row };
    }
  });

  canvas.addEventListener('mouseleave', () => {
    if (hoveredSquare && hoverTrailAmount > 0) {
      trailCells.unshift({ ...hoveredSquare });
      if (trailCells.length > hoverTrailAmount) trailCells.length = hoverTrailAmount;
    }
    hoveredSquare = null;
  });

  animId = requestAnimationFrame(animate);

  return () => {
    cancelAnimationFrame(animId);
    window.removeEventListener('resize', resize);
  };
}
