// Keyboard navigation, matching the TUI: arrows, Enter, Escape.
(function () {
  const navigableItems = () => [...document.querySelectorAll("main [data-nav]")];

  function focusFirstItem(container = document) {
    const target =
      container.querySelector("[autofocus]") ||
      [...container.querySelectorAll("[data-nav]")].find(
        (item) => item.tagName !== "INPUT"
      );
    if (target) {
      target.focus({ preventScroll: true });
    }
  }

  function moveFocus(direction) {
    const items = navigableItems();
    if (items.length === 0) {
      return;
    }
    const index = items.indexOf(document.activeElement);
    const next = index === -1 ? 0 : (index + direction + items.length) % items.length;
    items[next].focus();
    items[next].scrollIntoView({ block: "nearest" });
  }

  document.addEventListener("keydown", (event) => {
    if (event.altKey || event.ctrlKey || event.metaKey) {
      return;
    }

    const element = document.activeElement;
    const insideActions = element && element.closest(".dialog-actions");

    if (event.key === "Escape") {
      const back = document.querySelector("[data-back]");
      if (back) {
        event.preventDefault();
        back.click();
      }
    } else if (event.key === "ArrowDown" || (insideActions && event.key === "ArrowRight")) {
      event.preventDefault();
      moveFocus(1);
    } else if (event.key === "ArrowUp" || (insideActions && event.key === "ArrowLeft")) {
      event.preventDefault();
      moveFocus(-1);
    } else if (event.key === "PageDown") {
      const next = document.querySelector("[data-page-next]");
      if (next) {
        event.preventDefault();
        next.click();
      }
    } else if (event.key === "PageUp") {
      const previous = document.querySelector("[data-page-previous]");
      if (previous) {
        event.preventDefault();
        previous.click();
      }
    }
  });

  document.addEventListener("htmx:afterSettle", (event) => {
    if (event.detail.target === document.body) {
      focusFirstItem();
    } else if (!document.activeElement || document.activeElement === document.body) {
      focusFirstItem(event.detail.target);
    }
  });

  focusFirstItem();
})();
