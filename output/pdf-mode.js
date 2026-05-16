/* ========================================================================
 * pdf-mode.js — 학습자료 PDF 인쇄 모드 (2026-05-15)
 *
 * 동작:
 *  1. 페이지 로드 시 우상단에 "🖨 PDF 인쇄 모드" 토글 버튼 삽입
 *  2. 클릭 → body.print-mode 추가 + 해설을 맨 뒤 섹션으로 재배치
 *  3. "📄 인쇄 다이얼로그 열기" 버튼으로 window.print() 호출
 *  4. "❌ 일반 보기" 로 원상복구
 *
 * 모든 학습자료가 공통으로 참조 — 자료 자체는 수정 불요.
 * ========================================================================
 */
(function () {
  'use strict';

  // KaTeX 렌더링이 끝난 뒤 실행하도록 약간 지연
  window.addEventListener('DOMContentLoaded', function () {
    setTimeout(init, 200);
  });

  function init() {
    insertToolbar();
    insertBanner();
  }

  function insertToolbar() {
    const bar = document.createElement('div');
    bar.className = 'pdf-toolbar';
    bar.innerHTML = `
      <button id="pdfModeToggle" type="button">🖨 PDF 인쇄 모드</button>
    `;
    document.body.appendChild(bar);

    document.getElementById('pdfModeToggle').addEventListener('click', togglePrintMode);
  }

  function insertBanner() {
    const banner = document.createElement('div');
    banner.className = 'print-mode-banner';
    banner.innerHTML = '🖨 PDF 인쇄 모드 — 해설은 뒷장에 모았습니다. Ctrl/Cmd + P 로 PDF로 저장하세요.';
    document.body.insertBefore(banner, document.body.firstChild);
  }

  let printModeOn = false;
  let detachedDetails = []; // 원복 시 사용

  function togglePrintMode() {
    if (!printModeOn) {
      enablePrintMode();
    } else {
      disablePrintMode();
    }
  }

  function enablePrintMode() {
    document.body.classList.add('print-mode');
    relocateAnswers();
    updateToolbar(true);
    printModeOn = true;
    window.scrollTo(0, 0);
  }

  function disablePrintMode() {
    document.body.classList.remove('print-mode');
    restoreAnswers();
    updateToolbar(false);
    printModeOn = false;
  }

  /**
   * 각 .problem-card 안의 <details> 를 추출해 별도 .answer-section 에 모은다.
   * 카드 내부에는 "정답·해설은 뒷장 참고" placeholder 만 남긴다.
   */
  function relocateAnswers() {
    detachedDetails = [];

    // 1) 정답·해설 섹션 컨테이너 만들기 (없으면 추가)
    let answerSection = document.querySelector('.answer-section');
    if (!answerSection) {
      answerSection = document.createElement('section');
      answerSection.className = 'answer-section';
      answerSection.innerHTML = `
        <div class="answer-cover">📝 정답 · 풀이</div>
      `;
      // .container 의 끝에 붙임
      const container = document.querySelector('.container');
      if (container) container.appendChild(answerSection);
      else document.body.appendChild(answerSection);
    } else {
      // 이미 있는 경우 cover 외 모든 내용 지우고 다시 채움
      answerSection.querySelectorAll('.answer-block').forEach(el => el.remove());
    }

    // 2) 각 문제 카드 순회
    const problemCards = document.querySelectorAll('.problem-card');
    problemCards.forEach((card, idx) => {
      const details = card.querySelector('details');
      if (!details) return;

      const problemNum = card.querySelector('.problem-num');
      const title = problemNum ? problemNum.textContent.trim() : `문제 ${idx + 1}`;

      // <summary> 제거하고 .solution 만 추출
      const solution = details.querySelector('.solution');
      const solutionClone = solution ? solution.cloneNode(true) : null;

      // 원본을 잠시 비활성 (display:none) — 일반 모드 복귀 시 그대로
      details.dataset.pdfDetached = '1';

      // answer-block 생성
      const block = document.createElement('div');
      block.className = 'answer-block';
      block.innerHTML = `<div class="a-title">${escapeHtml(title)}</div>`;
      if (solutionClone) block.appendChild(solutionClone);
      answerSection.appendChild(block);

      // 카드 안에 placeholder
      if (!card.querySelector('.answer-ref')) {
        const ref = document.createElement('div');
        ref.className = 'answer-ref';
        ref.textContent = '👉 정답·풀이는 뒷장 [정답·풀이] 섹션 참고';
        card.appendChild(ref);
      }

      detachedDetails.push(details);
    });
  }

  function restoreAnswers() {
    // answer-section 비우기
    const answerSection = document.querySelector('.answer-section');
    if (answerSection) {
      answerSection.querySelectorAll('.answer-block').forEach(el => el.remove());
    }

    // placeholder 제거
    document.querySelectorAll('.problem-card .answer-ref').forEach(el => el.remove());

    detachedDetails.forEach(d => { delete d.dataset.pdfDetached; });
    detachedDetails = [];
  }

  function updateToolbar(on) {
    const bar = document.querySelector('.pdf-toolbar');
    if (!bar) return;
    bar.innerHTML = on
      ? `<button id="pdfPrintBtn" type="button">📄 인쇄 / PDF 저장</button>
         <button id="pdfExitBtn" type="button" class="exit">❌ 일반 보기</button>`
      : `<button id="pdfModeToggle" type="button">🖨 PDF 인쇄 모드</button>`;

    if (on) {
      document.getElementById('pdfPrintBtn').addEventListener('click', function () {
        window.print();
      });
      document.getElementById('pdfExitBtn').addEventListener('click', togglePrintMode);
    } else {
      document.getElementById('pdfModeToggle').addEventListener('click', togglePrintMode);
    }
  }

  function escapeHtml(s) {
    return s.replace(/[&<>"']/g, c => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    })[c]);
  }
})();
