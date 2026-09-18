// digit 1..8 -> activate that tab position (1-indexed); digit 9 -> last tab.
// Mirrors Chrome's native Ctrl+1..8 / Ctrl+9 behavior.
chrome.runtime.onMessage.addListener((message, sender) => {
  if (message.type !== "switchTab" || !sender.tab) {
    return;
  }
  chrome.tabs.query({ windowId: sender.tab.windowId }, (tabs) => {
    tabs.sort((a, b) => a.index - b.index);
    const target = message.digit === 9 ? tabs[tabs.length - 1] : tabs[message.digit - 1];
    if (target) {
      chrome.tabs.update(target.id, { active: true });
    }
  });
});
