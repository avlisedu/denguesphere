// Fundo animado da página Início: casos que se agrupam em clusters e se dispersam.
// Roda no documento principal (st.html com JavaScript) e se remove ao sair da página.
(() => {
    if (window.__dsClusterBg) return;

    const COLORS = [[13, 71, 161], [0, 131, 143], [0, 172, 193]]; // #0d47a1, #00838f, #00acc1
    const NEUTRAL = [120, 144, 156];
    const CYCLE = 8000;       // ms entre a formação de novos clusters
    const GATHER = 4200;      // ms em que os pontos ficam agrupados
    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    const canvas = document.createElement("canvas");
    canvas.setAttribute("aria-hidden", "true");
    Object.assign(canvas.style, {
        position: "fixed",
        inset: "0",
        width: "100vw",
        height: "100vh",
        zIndex: "-1",
        pointerEvents: "none",
    });
    document.body.appendChild(canvas);
    const ctx = canvas.getContext("2d");

    let W = 0, H = 0, points = [], clusters = [], lastCycle = -Infinity, missingSince = null, running = true;

    const rand = (a, b) => a + Math.random() * (b - a);
    const lerp = (a, b, t) => a + (b - a) * t;
    const rgba = (c, a) => `rgba(${c[0]}, ${c[1]}, ${c[2]}, ${a})`;

    function resize() {
        const dpr = window.devicePixelRatio || 1;
        W = window.innerWidth;
        H = window.innerHeight;
        canvas.width = W * dpr;
        canvas.height = H * dpr;
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
        const count = Math.round(Math.min(110, Math.max(45, (W * H) / 16000)));
        while (points.length < count) {
            points.push({
                x: rand(0, W), y: rand(0, H),
                vx: rand(-0.15, 0.15), vy: rand(-0.15, 0.15),
                cluster: -1, ox: 0, oy: 0, mix: 0,
            });
        }
        points.length = count;
    }

    // Escolhe novos centros e atrai os pontos mais próximos de cada um
    function formClusters(now) {
        const radius = Math.min(W, H) * 0.09;
        clusters = [];
        for (let tries = 0; clusters.length < 3 && tries < 200; tries++) {
            const c = { x: rand(W * 0.08, W * 0.92), y: rand(H * 0.15, H * 0.9), r: radius, color: COLORS[clusters.length] };
            if (clusters.every(o => Math.hypot(o.x - c.x, o.y - c.y) > radius * 4)) clusters.push(c);
        }
        points.forEach(p => (p.cluster = -1));
        clusters.forEach((c, i) => {
            points
                .filter(p => p.cluster < 0)
                .sort((a, b) => Math.hypot(a.x - c.x, a.y - c.y) - Math.hypot(b.x - c.x, b.y - c.y))
                .slice(0, Math.round(points.length * 0.2))
                .forEach(p => {
                    p.cluster = i;
                    const ang = rand(0, Math.PI * 2), dist = Math.abs(rand(-1, 1) * rand(0, 1)) * c.r;
                    p.ox = Math.cos(ang) * dist;
                    p.oy = Math.sin(ang) * dist;
                });
        });
        lastCycle = now;
    }

    function step(now) {
        if (!running) return;

        // Sai da página Início: remove o fundo
        if (!document.querySelector(".ds-home-title")) {
            missingSince ??= now;
            if (now - missingSince > 1000) return destroy();
        } else {
            missingSince = null;
        }

        if (now - lastCycle > CYCLE) formClusters(now);
        const gathering = now - lastCycle < GATHER;

        ctx.clearRect(0, 0, W, H);

        // Halos suaves em volta dos clusters
        clusters.forEach(c => {
            const members = points.filter(p => p.cluster >= 0 && clusters[p.cluster] === c);
            const strength = members.reduce((s, p) => s + p.mix, 0) / Math.max(1, members.length);
            if (strength < 0.02) return;
            const g = ctx.createRadialGradient(c.x, c.y, 0, c.x, c.y, c.r * 1.8);
            g.addColorStop(0, rgba(c.color, 0.10 * strength));
            g.addColorStop(1, rgba(c.color, 0));
            ctx.fillStyle = g;
            ctx.beginPath();
            ctx.arc(c.x, c.y, c.r * 1.8, 0, Math.PI * 2);
            ctx.fill();
        });

        points.forEach(p => {
            const inCluster = gathering && p.cluster >= 0;
            if (inCluster) {
                const c = clusters[p.cluster];
                p.vx += (c.x + p.ox - p.x) * 0.0016;
                p.vy += (c.y + p.oy - p.y) * 0.0016;
            } else {
                p.vx += rand(-0.012, 0.012);
                p.vy += rand(-0.012, 0.012);
            }
            p.vx *= 0.965;
            p.vy *= 0.965;
            p.x += p.vx;
            p.y += p.vy;
            if (p.x < -10) p.x = W + 10; else if (p.x > W + 10) p.x = -10;
            if (p.y < -10) p.y = H + 10; else if (p.y > H + 10) p.y = -10;
            p.mix = lerp(p.mix, inCluster ? 1 : 0, 0.025);
        });

        // Ligações finas entre vizinhos do mesmo cluster
        ctx.lineWidth = 0.7;
        for (let i = 0; i < points.length; i++) {
            const a = points[i];
            if (a.cluster < 0 || a.mix < 0.05) continue;
            for (let j = i + 1; j < points.length; j++) {
                const b = points[j];
                if (b.cluster !== a.cluster) continue;
                const d = Math.hypot(a.x - b.x, a.y - b.y);
                const reach = clusters[a.cluster].r * 0.7;
                if (d < reach) {
                    ctx.strokeStyle = rgba(clusters[a.cluster].color, 0.18 * Math.min(a.mix, b.mix) * (1 - d / reach));
                    ctx.beginPath();
                    ctx.moveTo(a.x, a.y);
                    ctx.lineTo(b.x, b.y);
                    ctx.stroke();
                }
            }
        }

        points.forEach(p => {
            const color = p.cluster >= 0 ? clusters[p.cluster].color : NEUTRAL;
            const c = [0, 1, 2].map(k => lerp(NEUTRAL[k], color[k], p.mix));
            ctx.fillStyle = rgba(c, 0.3 + 0.3 * p.mix);
            ctx.beginPath();
            ctx.arc(p.x, p.y, 2 + p.mix * 1.2, 0, Math.PI * 2);
            ctx.fill();
        });

        if (!reduceMotion) requestAnimationFrame(step);
    }

    function destroy() {
        running = false;
        window.removeEventListener("resize", resize);
        canvas.remove();
        delete window.__dsClusterBg;
    }

    window.__dsClusterBg = { destroy };
    window.addEventListener("resize", resize);
    resize();

    if (reduceMotion) {
        // Sem animação: mostra um quadro estático já agrupado
        formClusters(performance.now());
        points.forEach(p => {
            if (p.cluster >= 0) {
                const c = clusters[p.cluster];
                p.x = c.x + p.ox;
                p.y = c.y + p.oy;
                p.mix = 1;
            }
        });
    }
    requestAnimationFrame(step);
})();
