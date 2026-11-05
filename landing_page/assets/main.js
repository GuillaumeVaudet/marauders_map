// Links a field of the record explorer to its bytes, and tracks the current section.
(function () {
  // The track moves by half its width, so an even number of copies loops seamlessly.
  const TAPE_COPIES = 16;
  for (const track of document.querySelectorAll(".tape-track")) {
    const item = track.firstElementChild;
    for (let copy = 1; copy < TAPE_COPIES; copy++) {
      track.append(item.cloneNode(true));
    }
    track.classList.add("is-rolling");
  }

  const explorer = document.getElementById("record-explorer");
  const fields = [...explorer.querySelectorAll(".field")];
  const bytes = [...explorer.querySelectorAll(".hex span")];

  function select(id) {
    for (const field of fields) {
      const selected = field.dataset.field === id;
      field.classList.toggle("is-on", selected);
      field.setAttribute("aria-pressed", String(selected));
    }
    for (const byte of bytes) {
      byte.classList.toggle("is-on", byte.dataset.field === id);
    }
  }

  function fieldIdFrom(event) {
    return event.target.closest("[data-field]")?.dataset.field;
  }

  for (const eventName of ["mouseover", "focusin", "click"]) {
    explorer.addEventListener(eventName, (event) => {
      const id = fieldIdFrom(event);
      if (id) {
        select(id);
      }
    });
  }

  select("bssid");

  const tabs = new Map(
    [...document.querySelectorAll(".tab")].map((tab) => [tab.getAttribute("href").slice(1), tab])
  );
  const tabList = document.querySelector(".tabs");
  const observer = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (entry.isIntersecting) {
          for (const tab of tabs.values()) {
            tab.classList.remove("is-active");
          }
          // The hero has no tab: nothing stays active once back at the top.
          const active = tabs.get(entry.target.id);
          if (active) {
            active.classList.add("is-active");
            tabList.scrollLeft = active.offsetLeft - tabList.offsetLeft;
          }
        }
      }
    },
    { rootMargin: "-30% 0px -65% 0px" }
  );
  for (const id of ["top", ...tabs.keys()]) {
    observer.observe(document.getElementById(id));
  }
})();
