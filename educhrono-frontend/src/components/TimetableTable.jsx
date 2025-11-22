import React from "react";

const TimetableTable = ({ timetable, days, timeSlots }) => {
  const normalize = (t) => t?.replace(/–/g, "-").trim();

  const typeStyles = {
    L: { bg: "bg-white", icon: "📖" },
    T: { bg: "bg-blue-50", icon: "📘" },
    P: { bg: "bg-green-50", icon: "🧪" },
    COE: { bg: "bg-orange-50", icon: "🏛️" },
    PDP: { bg: "bg-purple-50", icon: "🧠" },
  };

  const getEntryAt = (day, slot) =>
    timetable.filter(
      (e) =>
        e.day?.toLowerCase() === day.toLowerCase() &&
        normalize(e.time_slot) === normalize(slot)
    );

  return (
    <table className="border-collapse border border-gray-400 w-full text-center text-sm">
      <thead className="bg-green-100">
        <tr>
          <th className="border border-gray-400 p-2 w-28">Day</th>
          {timeSlots.map((slot) => (
            <th
              key={slot}
              className="border border-gray-400 p-2 font-semibold text-gray-700"
            >
              {slot}
            </th>
          ))}
        </tr>
      </thead>

      <tbody>
        {days.map((day, dayIndex) => {
          let skipNext = false;

          return (
            <tr key={day}>
              <td className="border border-gray-400 p-2 font-semibold bg-gray-50">
                {day}
              </td>

              {timeSlots.map((slot, slotIndex) => {
                if (skipNext) {
                  skipNext = false;
                  return null;
                }

                // LUNCH BREAK merged column
                if (slot === "1:00–2:00") {
                  if (dayIndex === 0) {
                    return (
                      <td
                        key="lunch"
                        rowSpan={days.length}
                        className="border border-gray-400 bg-yellow-100 font-semibold text-gray-900 align-middle"
                      >
                        🍱 LUNCH BREAK
                      </td>
                    );
                  }
                  return null;
                }

                const entries = getEntryAt(day, slot);

                if (entries.length === 0)
                  return (
                    <td key={`${day}-${slot}`} className="border border-gray-400 text-gray-500">
                      -
                    </td>
                  );

                const e0 = entries[0];

                // Detect 2-hour block (T/P/COE merged)
                const isTwoHour =
                  e0.type === "T" ||
                  e0.type === "P" ||
                  (e0.isGroupSplit === false &&
                    e0.time_slot &&
                    timetable.some(
                      (x) =>
                        x.time_slot === e0.time_slot &&
                        x.section === e0.section &&
                        x.type === e0.type &&
                        x.slot2
                    )) ||
                  e0.slot2;

                if (isTwoHour) {
                  skipNext = true;

                  const { bg, icon } = typeStyles[e0.type] || {};

                  // Grouped T/P — multiple entries inside
                  if (entries.every((a) => a.isGroupSplit)) {
                    return (
                      <td
                        key={`${day}-${slot}-2h-group`}
                        colSpan={2}
                        className={`border border-gray-400 p-2 whitespace-pre-line ${bg}`}
                      >
                        {entries.map((e, idx) => (
                          <div
                            key={idx}
                            className="mb-1 border-b border-gray-300 pb-1 last:border-0 rounded-md p-1"
                          >
                            <span className="font-semibold text-gray-900">
                              {icon} {e.subject} ({e.section})
                            </span>
                            <div className="text-gray-700">{e.room}</div>
                            <div className="text-gray-500 text-xs">{e.faculty}</div>
                          </div>
                        ))}
                      </td>
                    );
                  }

                  // Non-group 2-hour entries (COE, sometimes lab)
                  return (
                    <td
                      key={`${day}-${slot}-2h`}
                      colSpan={2}
                      className={`border border-gray-400 p-2 whitespace-pre-line ${bg}`}
                    >
                      <div className="mb-1 rounded-md p-1">
                        <span className="font-semibold text-gray-900">
                          {icon} {e0.subject}
                        </span>
                        <div className="text-gray-700">{e0.room}</div>
                        <div className="text-gray-500 text-xs">{e0.faculty}</div>
                      </div>
                    </td>
                  );
                }

                // Standard (1-hour) entries
                return (
                  <td
                    key={`${day}-${slot}`}
                    className="border border-gray-400 p-2 whitespace-pre-line"
                  >
                    {entries.map((e, idx) => {
                      const { bg, icon } = typeStyles[e.type] || {};
                      return (
                        <div
                          key={idx}
                          className={`mb-1 border-b border-gray-300 pb-1 last:border-0 p-1 rounded-md ${bg}`}
                        >
                          <span className="font-semibold text-gray-900">
                            {icon} {e.subject}
                          </span>
                          <div className="text-gray-700">{e.room}</div>
                          <div className="text-gray-500 text-xs">{e.faculty}</div>
                        </div>
                      );
                    })}
                  </td>
                );
              })}
            </tr>
          );
        })}
      </tbody>
    </table>
  );
};

export default TimetableTable;
