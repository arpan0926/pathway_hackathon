/* =========================================================
   dashboard.js — enterprise-grade UI polish (enhanced)
   - Non-invasive, idempotent, Streamlit-safe
   - Improves perceived liveness without DOM hacks
   - Designed for auto-refresh dashboards
   ========================================================= */
/* ==================================================
   Clean, light-themed interaction helpers for Streamlit
   - idempotent, non-blocking, and resilient to re-renders
   - small: reveal cards, flash changed numbers, and equalize heights
   ================================================== */
(function (){
  'use strict';

  var idle = window.requestIdleCallback || function(fn){ return setTimeout(fn, 120); };
  var raf = window.requestAnimationFrame || function(fn){ return setTimeout(fn, 16); };
  var debounceTimer = null;

  function safeQuery(selector, root){
    try{ return Array.prototype.slice.call((root||document).querySelectorAll(selector)); }catch(e){ return []; }
  }

  function addBadge(){
    try{
      if(document.querySelector('.made-with')) return;
      var b = document.createElement('div');
      b.className = 'made-with';
      b.textContent = 'Real-Time Supply Chain • Streamlit demo';
      document.body.appendChild(b);
    }catch(e){}
  }

  function reveal(){
    try{
      var nodes = safeQuery('.dashboard-card.fade-on-load, .dashboard-header.fade-on-load');
      for(var i=0;i<nodes.length;i++){
        var el = nodes[i];
        if(!el.classList.contains('is-visible')){
          (function(e, delay){ setTimeout(function(){ e.classList.add('is-visible'); }, delay); })(el, (i%6)*60);
        }
      }
    }catch(e){}
  }

  var previous = new WeakMap();
  function scanNumbers(){
    try{
      var nodes = safeQuery('.dashboard-card span, .dashboard-card div, .dashboard-card p');
      var count = 0;
      for(var i=0;i<nodes.length && count<180;i++){
        var n = nodes[i];
        var txt = (n.textContent||'').trim();
        if(!/\d/.test(txt) || txt.length>30) continue;
        var norm = txt.replace(/[\u00A0\s]+/g,' ').replace(/[^0-9.,\-]/g,'').trim();
        if(!norm) continue;
        var prev = previous.get(n);
        if(prev && prev !== norm){
          n.classList.add('num-flash');
          (function(el){ setTimeout(function(){ el.classList.remove('num-flash'); }, 900); })(n);
        }
        previous.set(n, norm);
        count++;
      }
    }catch(e){}
  }

  /* Equalize heights: ensure right-column cards don't collapse relative to map */
  function equalizeHeights(){
  try{
      // Skip equalization on small screens (let flow stack naturally)
      var vw = Math.max(document.documentElement.clientWidth || 0, window.innerWidth || 0);
      if(vw < 900){
        // remove any previous inline min-height we set
        var prev = safeQuery('.dashboard-card');
        for(var p=0;p<prev.length;p++){ prev[p].style.minHeight = ''; }
        return;
      }

      // optional debug flag (set localStorage.setItem('st_ui_debug','1') to enable)
      var debug = false;
      try{ debug = !!(localStorage && localStorage.getItem && localStorage.getItem('st_ui_debug') === '1'); }catch(e){}

      // clear any previously applied heights so we measure fresh
      var allCards = safeQuery('.dashboard-card');
      for(var i=0;i<allCards.length;i++){ allCards[i].style.minHeight = ''; }

      var maps = safeQuery('.live-map');
      if(!maps.length) return;

      // For each map, find cards that are in the same horizontal row (similar top offset)
      for(var m=0;m<maps.length;m++){
        var lm = maps[m];
        var lmRect = lm.getBoundingClientRect();
        var lmTop = Math.round(lmRect.top);
        var lmH = Math.round(lmRect.height);
        if(debug) console.debug('live-map', m, 'top', lmTop, 'height', lmH);

        // Find candidate cards that sit roughly at the same top offset
        for(var j=0;j<allCards.length;j++){
          var c = allCards[j];
          if(c === lm) continue;
          var r = c.getBoundingClientRect();
          var topDiff = Math.abs(Math.round(r.top) - lmTop);
          // same row if top difference small (tolerance 48px)
          if(topDiff <= 48){
            // only increase minHeight when map is taller than card
            if(lmH > (r.height + 6)){
              c.style.minHeight = (lmH - 6) + 'px';
              if(debug) console.debug('  set minHeight for', c, '->', c.style.minHeight);
            }
          }
        }
      }

    }catch(e){ if(window && window.console) console.debug && console.debug('equalizeHeights error', e); }
  }

  /* Match live-map height to the 'Key metrics' card height when present
     This ensures the left map visually lines up with the key metrics card. */
  function matchMapToMetrics(){
    try{
      var vw = Math.max(document.documentElement.clientWidth || 0, window.innerWidth || 0);
      if(vw < 900) return; // on small screens, let natural flow

      var cards = safeQuery('.dashboard-card');
      if(!cards.length) return;

      // find the card that contains the heading 'Key metrics' (case-insensitive)
      var metricsCard = null;
      for(var i=0;i<cards.length;i++){
        try{ if(/key\s*metrics/i.test(cards[i].textContent || '')){ metricsCard = cards[i]; break; } }catch(e){}
      }
      if(!metricsCard) return;

      var metricsRect = metricsCard.getBoundingClientRect();
      var targetH = Math.round(metricsRect.height);
      if(!targetH) return;

      var maps = safeQuery('.live-map');
      for(var m=0;m<maps.length;m++){
        var lm = maps[m];
        // apply with a small buffer so visuals don't clip
        lm.style.minHeight = (targetH + 8) + 'px';
      }
    }catch(e){ if(window && window.console) console.debug && console.debug('matchMapToMetrics error', e); }
  }

  function applyAll(){
    idle(function(){
      addBadge(); reveal(); scanNumbers(); equalizeHeights();
    });
  }

  function scheduleApply(){
    if(debounceTimer) clearTimeout(debounceTimer);
    debounceTimer = setTimeout(function(){ raf(applyAll); debounceTimer = null; }, 80);
  }

  // Observe DOM changes from Streamlit re-renders and re-apply effects
  function observe(){
    try{
      var mo = new MutationObserver(function(m){ scheduleApply(); });
      mo.observe(document.body, { childList:true, subtree:true });
      // run once immediately
      scheduleApply();
    }catch(e){}
  }

  if(document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', function(){ applyAll(); observe(); });
  } else { applyAll(); observe(); }

})();

