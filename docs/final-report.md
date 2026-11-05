# Marauder's Map — Final Report


## 1. Results summary

### 1.1 What the MVP delivers

The MVP is a complete chain from radio capture to map, working on both the hardware
and the software side.

- **Capture device:** one ESP32-C5 node captures Wi-Fi beacon frames and sends them
  over ESP-NOW to a core unit, which adds the GPS position and time and records them
  on a microSD card.
- **Import:** binary capture files are decoded into one SQLite database per city, and
  a file that was already imported is skipped.
- **Exploration:** networks, observations and statistics can be viewed in a terminal
  interface (TUI) or a local web interface (GUI).
- **Map (GUI):** networks are displayed on an offline map, with clustering and a filter
  by encryption level.
- **Data management:** databases can be created and deleted, and imported files listed.

### 1.2 Comparison with the initial objectives

| Initial objective | Outcome | Status |
| --- | --- | --- |
| Device with 4 capture nodes | 1 node built | ⏳ Partial, remaining nodes deferred |
| Wi-Fi capture | Beacon frames on 2.4 GHz | ✅ Achieved |
| Bluetooth and BLE capture | Not implemented | ⏳ Deferred |
| GPS position for each capture | Implemented | ✅ Achieved |
| Recording in CSV | Binary format on microSD instead | 🔄 Changed, CSV planned as an export |
| Web GUI | Implemented | ✅ Achieved |
| Interactive map | Implemented | ✅ Achieved |

Scope was deliberately narrowed to Wi-Fi frames so that one full chain would work from
end to end. The deferred items are not abandoned and will be added progressively. The
capture format already reserves what they need: `node_id` accepts values 1 to 4, and
`band` has a value for BLE.

### 1.3 Key metrics

| Metric | Value |
| --- | --- |
| Reference field capture | 83 minutes, 42 MB |
| Networks detected | 4,997 |
| Observations recorded | 128,140 |
| Observations with a GPS position | 127,486 (99.5%) |
| Import time of the reference capture | About 0.7 s (measured on RAM-backed storage) |
| Application code | About 1,600 lines of Python, plus about 800 of templates and JavaScript |
| Automated tests | 0 (manual verification only) |
| External user tests | None: the tool is for personal use |

### 1.4 Presentation

The final presentation and live demo went well and covered all the requirements. There
were no questions afterwards because the content was clear. The feedback was that I
clearly enjoyed building this project and enjoy sharing it.

## 2. Lessons learned

### 2.1 What went well

- **First steps in electronics.** I relearned the basics of electricity and how to
  connect electronic modules together. This was the most enjoyable part of the project,
  and it brought back knowledge from my former military specialty in radio.
- **A working result on both sides.** The hardware and the software both work, and real
  captures from the device can be explored on a map.
- **Choosing Python.** Moving to a language I master let me iterate quickly and test
  more ideas (see below).

### 2.2 Challenges and how they were addressed

| Challenge | Response | Result |
| --- | --- | --- |
| The learning curve of Rust was too steep and slowed the project down | Moved to Python | Much faster execution and iteration, at the cost of no longer learning Rust through this project |
| The initial scope (4 nodes, Bluetooth, BLE) was too large for the time available | Focused on Wi-Fi frames with one node | A complete, working chain, with the rest deferred |
| Fragile hardware: my solder joints are not very clean or strong, and the device has no enclosure | Not resolved yet: a 3D-printed case is planned | Short-circuit and reliability risk during outings |
| No feedback from the device while capturing: I cannot tell whether it is working | Not resolved yet: a screen showing logs is planned | Limits how long an outing can safely be |

### 2.3 Known limitations

- **Hardware:** the solder quality, the missing enclosure and the lack of a capture
  status display listed above.
- **Software:** the [technical documentation](technical-documentation.md#91-known-defects)
  lists nine known defects. The most important is that some WPA networks are reported
  as WEP, which affects 17 networks in the reference capture. Others concern error
  handling in the TUI. None of them has been fixed yet.
- **Testing:** the repository has no automated tests, and the only user is the author.
- **To investigate:** 86% of the frames in the reference capture are on channel 6. This
  may come from the environment or from how the channels are scanned.

### 2.4 How to improve on future projects

- Size the initial scope against the time available, and plan the MVP as a first
  increment.
- Choose technologies I already master when the deadline is short, and learn a new
  language separately.
- Write automated tests alongside the code, rather than planning them afterwards.
- Include feedback and robustness in hardware design from the start.
- Ask someone else to try the tool, even if it is for personal use.

### 2.5 Use of AI

AI assistance was used to quickly obtain the cyberpunk visual design of the web front
end, and to help write and check the project documentation.

## 3. Retrospective highlights

This was a solo project, so this is an individual retrospective rather than a team
meeting. The guiding questions are adapted accordingly.

**What worked well?**

Enjoying the subject kept me motivated, especially on the hardware side. Delivering one
complete chain, rather than several unfinished features, gave a usable result.

**What challenges were faced, and how were they resolved?**

The two main ones were speed of progress, resolved by moving to Python and narrowing the
scope, and hardware robustness, which is still open and has a concrete plan.

**How can collaboration improve in the future?**

Working alone meant that no one else reviewed the code or tried the application. On
future projects, I would ask for a peer review or a test session before the final stage.

## 4. Next steps

1. **Harden the device:** improve the solder joints and design a 3D-printed case to
   contain the electronics and prevent short circuits.
2. **Add a screen with logs,** to see during capture whether something is wrong, which
   will allow longer outings.
3. **Extend capture progressively:** up to 4 nodes, then Bluetooth and BLE.
4. **Fix the known software defects** and add automated tests.
5. **Add exports,** including CSV.

## 5. Acknowledgments

Thanks to Mathieu M., our SWE; to Anthony, the school's director of pedagogy; and to my
classmates Elliot and Maxime.
