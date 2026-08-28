/* ========================================================================
 * pdf-mode.js — 학습자료 PDF 인쇄 모드
 *
 * 인쇄 전에 두 가지 중 고른다.
 *   ① 해설 함께  — 문항 바로 아래에 정답·풀이를 펼쳐서 출력 (교사용/자습용)
 *   ② 해설 뒤로  — 문항만 앞에, 정답·풀이는 맨 뒤 [정답·풀이] 섹션에 모아 출력
 *                  (학생 배포용 — 앞장은 문제지, 뒷장은 답지)
 *
 * 2026-08-27 개편
 *   - 문항 셀렉터가 .problem-card(A형 템플릿)만 보고 있어, article.problem 을
 *     쓰는 B형 자료 29편에서는 재배치가 아예 일어나지 않았다. 그런데도 배너는
 *     "해설은 뒷장에 모았습니다"라고 말해 설명과 실제가 어긋났다.
 *     → 두 템플릿을 모두 잡도록 셀렉터를 넓히고, 문항 제목 추출도 폴백을 뒀다.
 *   - 문구가 실제 동작을 따라가도록 배너를 선택에 맞춰 갱신한다.
 *
 * 모든 학습자료가 이 파일 하나를 참조하므로, 여기만 고치면 전 자료에 일관 적용된다.
 * ========================================================================
 */
(function () {
  'use strict';

  // A형(하이브리드 스켈레톤)과 B형(최근 템플릿)을 모두 잡는다.
  var PROBLEM_SEL = '.problem-card, article.problem';
  var MODE_KEY = 'pdf-answer-mode';        // 'back' | 'inline'

  // 워드마크 경로는 이 스크립트 위치에서 유도한다. 자료는 output/{학년}/{단원}/ 에
  // 있어 상대깊이가 고정이지만, 하드코딩하면 구조가 바뀔 때 조용히 깨진다.
  // currentScript 는 파싱 시점에만 유효하므로 지금 잡아 둔다.
  var SELF = document.currentScript;
  var WORDMARK = SELF
    ? SELF.src.replace(/pdf-mode\.js(?:\?.*)?$/, 'assets/brand/wordmark.png')
    : '../../assets/brand/wordmark.png';

  window.addEventListener('DOMContentLoaded', function () {
    setTimeout(init, 200);                 // KaTeX 렌더 뒤에 붙는다
  });

  var printModeOn = false;
  var answerMode = readMode();

  function readMode() {
    try { return localStorage.getItem(MODE_KEY) === 'inline' ? 'inline' : 'back'; }
    catch (_) { return 'back'; }
  }
  function saveMode(m) { try { localStorage.setItem(MODE_KEY, m); } catch (_) {} }

  function init() {
    insertToolbar();
    insertBanner();
    insertPrintFooter();
  }

  // 인쇄본 바닥글 — 종이에 브랜드가 남게. 화면에서는 CSS 로 숨긴다.
  // 예전엔 @page 의 @bottom-left 에 "학습자료 — youtube-math-skill" 텍스트를
  // 박아 뒀는데, 여백 상자에는 이미지를 안정적으로 넣을 수 없어 고정 요소로 바꿨다.
  function insertPrintFooter() {
    if (document.querySelector('.print-brand-footer')) return;
    var f = document.createElement('div');
    f.className = 'print-brand-footer';
    f.setAttribute('aria-hidden', 'true');   // 화면 낭독기에는 불필요한 장식

    var img = document.createElement('img');
    img.src = WORDMARK;
    img.alt = 'aftermath';
    f.appendChild(img);

    var handle = document.createElement('span');
    handle.textContent = '@irun20000';
    f.appendChild(handle);

    document.body.appendChild(f);
  }

  /* ---------------- 툴바 ---------------- */

  /**
   * 자료가 이미 가진 툴바(🏠 갤러리 · 🌙 다크모드 …) 안, 다크모드 바로 뒤에 끼워 넣는다.
   * 예전엔 화면 우상단에 고정으로 띄웠는데 난이도 필터(전체·기초·기본…)를 덮었다.
   * 툴바를 못 찾으면 예전처럼 우상단 고정으로 떨어진다.
   */
  function insertToolbar() {
    var bar = document.createElement('div');
    bar.className = 'pdf-toolbar';

    var darkBtn = findDarkButton();
    if (darkBtn && darkBtn.parentElement) {
      bar.classList.add('in-toolbar');
      darkBtn.parentElement.insertBefore(bar, darkBtn.nextSibling);
    } else {
      document.body.appendChild(bar);
    }
    renderToolbar();
  }

  function findDarkButton() {
    var byId = document.getElementById('darkModeToggle');
    if (byId) return byId;
    var all = document.querySelectorAll('.toolbar button, .controls button, header button');
    for (var i = 0; i < all.length; i++) {
      if (/다크/.test(all[i].textContent)) return all[i];
    }
    return null;
  }

  function renderToolbar() {
    var bar = document.querySelector('.pdf-toolbar');
    if (!bar) return;
    bar.textContent = '';

    if (!printModeOn) {
      bar.appendChild(btn('pdfModeToggle', '🖨 PDF 인쇄 모드', togglePrintMode));
      return;
    }

    // 인쇄 모드일 때만 선택지를 보여준다 — 평소엔 화면을 어지럽히지 않는다.
    var group = document.createElement('div');
    group.className = 'pdf-modes';
    group.setAttribute('role', 'group');
    group.setAttribute('aria-label', '정답·해설 출력 방식');

    group.appendChild(modeBtn('back', '해설 뒤로', '문항만 앞에, 정답·풀이는 맨 뒤에 모아 출력'));
    group.appendChild(modeBtn('inline', '해설 함께', '문항 바로 아래에 정답·풀이를 펼쳐 출력'));
    bar.appendChild(group);

    bar.appendChild(btn('pdfPrintBtn', '📄 인쇄 / PDF 저장', function () { window.print(); }));
    bar.appendChild(btn('pdfExitBtn', '❌ 일반 보기', togglePrintMode, 'exit'));
  }

  function btn(id, label, onClick, cls) {
    var b = document.createElement('button');
    b.type = 'button';
    b.id = id;
    b.textContent = label;
    if (cls) b.className = cls;
    b.addEventListener('click', onClick);
    return b;
  }

  function modeBtn(mode, label, title) {
    var b = document.createElement('button');
    b.type = 'button';
    b.className = 'pdf-mode-btn' + (answerMode === mode ? ' active' : '');
    b.textContent = label;
    b.title = title;
    b.setAttribute('aria-pressed', String(answerMode === mode));
    b.addEventListener('click', function () {
      if (answerMode === mode) return;
      answerMode = mode;
      saveMode(mode);
      applyAnswerMode();
      renderToolbar();
      updateBanner();
    });
    return b;
  }

  /* ---------------- 배너 ---------------- */

  function insertBanner() {
    var banner = document.createElement('div');
    banner.className = 'print-mode-banner';
    document.body.insertBefore(banner, document.body.firstChild);
    updateBanner();
  }

  // 문구가 실제 동작과 어긋나지 않도록 선택에 맞춰 다시 쓴다.
  function updateBanner() {
    var el = document.querySelector('.print-mode-banner');
    if (!el) return;
    el.textContent = answerMode === 'back'
      ? '🖨 PDF 인쇄 모드 — 문항만 앞에 나오고, 정답·풀이는 맨 뒤 [정답·풀이] 섹션에 모입니다. Ctrl/Cmd + P 로 저장하세요.'
      : '🖨 PDF 인쇄 모드 — 정답·풀이를 각 문항 바로 아래에 함께 출력합니다. Ctrl/Cmd + P 로 저장하세요.';
  }

  /* ---------------- 모드 전환 ---------------- */

  function togglePrintMode() {
    printModeOn = !printModeOn;
    document.body.classList.toggle('print-mode', printModeOn);
    if (printModeOn) {
      applyAnswerMode();
      window.scrollTo(0, 0);
    } else {
      restoreAnswers();
      document.body.classList.remove('answers-back', 'answers-inline');
    }
    renderToolbar();
    updateBanner();
  }

  function applyAnswerMode() {
    document.body.classList.toggle('answers-back', answerMode === 'back');
    document.body.classList.toggle('answers-inline', answerMode === 'inline');
    if (answerMode === 'back') relocateAnswers();
    else restoreAnswers();
  }

  /* ---------------- 해설 재배치 ---------------- */

  /**
   * 풀이를 복제해 맨 뒤 .answer-section 에 모으고, 원래 자리에는 "뒷장 참고" 안내만 남긴다.
   * 원본은 지우지 않고 CSS 로 숨기므로 일반 보기로 돌아가면 그대로 복구된다.
   *
   * 기준을 '문항 카드'가 아니라 **.solution 을 품은 details** 로 잡는다.
   * 카드 클래스를 열거하면(.problem-card, article.problem …) 도입 예시처럼 다른
   * 컨테이너(div.card)에 담긴 풀이가 그대로 남아, "뒷장에 모았다"는 말이 또 어긋난다.
   * 실제로 15편에서 도입 예시 풀이 1개가 본문에 남아 있었다.
   */
  function relocateAnswers() {
    var answerSection = document.querySelector('.answer-section');
    if (!answerSection) {
      answerSection = document.createElement('section');
      answerSection.className = 'answer-section';
      var cover = document.createElement('div');
      cover.className = 'answer-cover';
      cover.textContent = '📝 정답 · 풀이';
      answerSection.appendChild(cover);
      var container = document.querySelector('.container') || document.body;
      container.appendChild(answerSection);
    } else {
      answerSection.querySelectorAll('.answer-block').forEach(function (el) { el.remove(); });
    }

    var idx = 0;
    document.querySelectorAll('details').forEach(function (details) {
      if (details.closest('.answer-section')) return;      // 이미 답지 안
      var solution = details.querySelector('.solution');
      if (!solution) return;                               // 풀이가 없는 접힘은 그대로 둔다

      var host = details.closest(PROBLEM_SEL) || details.closest('.card') || details.parentElement;

      var block = document.createElement('div');
      block.className = 'answer-block';
      var t = document.createElement('div');
      t.className = 'a-title';
      t.textContent = problemTitle(host, idx);             // textContent 라 주입 여지 없음
      block.appendChild(t);
      block.appendChild(solution.cloneNode(true));
      answerSection.appendChild(block);

      // 숨김은 조상 구조에 기대지 않고 이 표시로 건다
      details.classList.add('pdf-relocated');

      if (host && !host.querySelector(':scope > .answer-ref')) {
        var ref = document.createElement('div');
        ref.className = 'answer-ref';
        ref.textContent = '👉 정답·풀이는 뒷장 [정답·풀이] 섹션 참고';
        host.appendChild(ref);
      }
      idx++;
    });
  }

  // A형은 .problem-num, B형·도입 카드는 <h3>. 둘 다 없으면 번호로 떨어진다.
  function problemTitle(host, idx) {
    var el = host && (host.querySelector('.problem-num') || host.querySelector('h3'));
    var t = el ? el.textContent.trim() : '';
    return t || ('문제 ' + (idx + 1));
  }

  function restoreAnswers() {
    var sec = document.querySelector('.answer-section');
    if (sec) sec.querySelectorAll('.answer-block').forEach(function (el) { el.remove(); });
    document.querySelectorAll('.answer-ref').forEach(function (el) { el.remove(); });
    document.querySelectorAll('details.pdf-relocated').forEach(function (d) {
      d.classList.remove('pdf-relocated');
    });
  }
})();
