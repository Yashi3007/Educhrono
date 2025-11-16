import React from "react";

const TimetableTable = ({ timetable, days, timeSlots }) => {
  const normalizeTime = (time) => time?.replace(/–/g, "-").trim();

  const typeStyles = {
    L: { bg: "bg-white", icon: "📖" },
    T: { bg: "bg-blue-50", icon: "📘" },
    P: { bg: "bg-green-50", icon: "🧪" },
    COE: { bg: "bg-orange-50", icon: "🏛️" },
    PDP: { bg: "bg-purple-50", icon: "🧠" },
  };

  return (
    <table className="border-collapse border border-gray-400 w-full text-center text-sm">
      <thead className="bg-green-100">
        <tr>
          <th className="border border-gray-400 p-2 w-28">Day</th>
          {timeSlots.map((slot) => (
            <th
              key={slot}
              className="border border-gray-400 p-2 text-sm font-semibold text-gray-700"
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

                // 🍱 Lunch Break cell (single merged column)
                if (slot === "1:00–2:00") {
                  if (dayIndex === 0)
                    return (
                      <td
                        key="lunch"
                        rowSpan={days.length}
                        className="border border-gray-400 bg-yellow-100 font-semibold text-gray-800 text-center align-middle"
                      >
                        🍱 LUNCH BREAK
                      </td>
                    );
                  return null;
                }

                // 🔍 Find entries for this day and slot
                const oneHourEntries = timetable.filter(
                  (t) =>
                    t.day?.toLowerCase() === day.toLowerCase() &&
                    normalizeTime(t.time_slot)?.toLowerCase() ===
                      normalizeTime(slot)?.toLowerCase()
                );

                // 🧪 Find if there’s a 2-hour (merged) class starting here
                const twoHourEntries = timetable.filter(
                  (t) =>
                    t.day?.toLowerCase() === day.toLowerCase() &&
                    normalizeTime(t.time_slot)?.startsWith(
                      normalizeTime(slot)
                    ) &&
                    (t.time_slot?.includes("+") ||
                      ["P", "T", "COE"].includes(t.type))
                );

                // 🎯 Render merged 2-hour cell
                if (twoHourEntries.length > 0) {
                  skipNext = true;
                  const { type } = twoHourEntries[0];
                  const { bg, icon } = typeStyles[type] || {};
                  return (
                    <td
                      key={`${day}-${slot}-double`}
                      colSpan={2}
                      className={`border border-gray-400 p-2 whitespace-pre-line ${bg}`}
                    >
                      {twoHourEntries.map((entry, idx) => (
                        <div
                          key={idx}
                          className="mb-1 border-b border-gray-300 pb-1 last:border-0 rounded-md p-1"
                        >
                          <span className="block font-semibold text-gray-900">
                            {icon} {entry.subject} ({entry.type}
                            {entry.batch ? ` - ${entry.batch}` : ""})
                          </span>
                          <span className="block text-gray-700">
                            {entry.room}
                          </span>
                          <span className="block text-gray-500 text-xs">
                            {entry.faculty}
                          </span>
                        </div>
                      ))}
                    </td>
                  );
                }

                // 📘 Single 1-hour class or empty slot
                if (oneHourEntries.length === 0)
                  return (
                    <td
                      key={`${day}-${slot}`}
                      className="border border-gray-400 text-gray-500"
                    >
                      -
                    </td>
                  );

                return (
                  <td
                    key={`${day}-${slot}`}
                    className="border border-gray-400 p-2 whitespace-pre-line"
                  >
                    {oneHourEntries.map((entry, idx) => {
                      const { bg, icon } = typeStyles[entry.type] || {};
                      return (
                        <div
                          key={idx}
                          className={`mb-1 border-b border-gray-300 pb-1 last:border-0 rounded-md p-1 ${bg}`}
                        >
                          <span className="block font-semibold text-gray-900">
                            {icon} {entry.subject} ({entry.type}
                            {entry.batch ? ` - ${entry.batch}` : ""})
                          </span>
                          <span className="block text-gray-700">
                            {entry.room}
                          </span>
                          <span className="block text-gray-500 text-xs">
                            {entry.faculty}
                          </span>
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
