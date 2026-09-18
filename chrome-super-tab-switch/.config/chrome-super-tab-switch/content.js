// Intercepts Super(Meta)+1..9 before the page sees it and asks the
// background service worker to switch tabs. Chrome's own commands API can't
// bind the Super/Meta key at all (only Ctrl/Alt/Shift), so this is done as a
// plain keydown listener instead of a manifest "commands" shortcut.
document.addEventListener(
  "keydown",
  (event) => {
    if (event.ctrlKey || event.altKey || event.shiftKey || !event.metaKey) {
      return;
    }
    const match = /^Digit([1-9])$/.exec(event.code);
    if (!match) {
      return;
    }
    event.preventDefault();
    event.stopImmediatePropagation();
    chrome.runtime.sendMessage({ type: "switchTab", digit: Number(match[1]) });
  },
  true,
);
