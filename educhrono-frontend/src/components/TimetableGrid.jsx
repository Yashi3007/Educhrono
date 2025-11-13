import React, { useRef } from "react";
import html2canvas from "html2canvas";
import jsPDF from "jspdf";

export default function TimetableGrid({
  timetable,
  facultyName,
  role,
  semester,
  section,
}) {
  const tableRef = useRef();

  const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];
  const normalizeTime = (time) => time?.replace(/–/g, "-").trim();

  const slots = [
    "9:00-10:00",
    "10:00-11:00",
    "11:00-12:00",
    "12:00-1:00",
    "2:00-3:00",
    "3:00-4:00",
  ];

  // 📄 Download PDF
  const handleDownload = async () => {
    const table = tableRef.current;
    const canvas = await html2canvas(table, { scale: 2 });
    const imgData = canvas.toDataURL("image/png");

    const pdf = new jsPDF("landscape", "mm", "a4");
    const width = pdf.internal.pageSize.getWidth() - 20;
    const height = (canvas.height * width) / canvas.width;

    // Header
    pdf.setFont("helvetica", "bold");
    pdf.setFontSize(16);
    pdf.text(
      "EduChrono | Weekly Timetable",
      pdf.internal.pageSize.getWidth() / 2,
      15,
      { align: "center" }
    );

    pdf.setFont("helvetica", "normal");
    pdf.setFontSize(11);

    if (role === "faculty") pdf.text(`Faculty: ${facultyName}`, 15, 25);
    if (role === "student")
      pdf.text(`Semester: ${semester} | Section: ${section}`, 15, 25);

    // Add timetable image
    pdf.addImage(imgData, "PNG", 10, 35, width, height);
    pdf.save(`Timetable_${facultyName || "Schedule"}.pdf`);
  };

  return (
    <div className="bg-white p-5 rounded-lg shadow-md">
      {/* Download PDF button */}
      <div className="flex justify-end mb-4">
        <button
          onClick={handleDownload}
          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition"
        >
          📄 Download Timetable
        </button>
      </div>

      {/* Timetable grid */}
      <div ref={tableRef} className="overflow-x-auto">
        <table className="border-collapse border border-gray-400 w-full text-center">
          <thead className="bg-blue-50">
            <tr>
              <th className="border p-2 w-24">Time</th>
              {days.map((day) => (
                <th key={day} className="border p-2">
                  {day}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {slots.map((slot) => (
              <tr key={slot}>
                <td className="border p-2 font-semibold bg-gray-50">{slot}</td>
                {days.map((day) => {
                  const cleanSlot = normalizeTime(slot);
                  const lecture = timetable?.[day]?.[cleanSlot];
                  return (
                    <td key={day + slot} className="border p-2 text-sm">
                      {lecture ? (
                        <>
                          <div className="font-semibold">{lecture.subject}</div>
                          <div className="text-xs text-gray-600">
                            {lecture.room}
                          </div>
                          <div className="text-xs text-gray-500">
                            {lecture.section}
                          </div>
                        </>
                      ) : (
                        "-"
                      )}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
