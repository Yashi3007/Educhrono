import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";
import { useState, useEffect, useRef } from "react";
import API from "../services/api";
import html2canvas from "html2canvas";
import jsPDF from "jspdf";

const DashboardHOD = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const [records, setRecords] = useState([]);
  const [timetable, setTimetable] = useState([]);
  const [filteredTimetable, setFilteredTimetable] = useState([]);
  const [loading, setLoading] = useState(false);

  const [facultyList, setFacultyList] = useState([]);
  const [sectionList, setSectionList] = useState([]);
  const [semesterList, setSemesterList] = useState([]);

  const [selectedFaculty, setSelectedFaculty] = useState("");
  const [selectedSection, setSelectedSection] = useState("");
  const [selectedSemester, setSelectedSemester] = useState("");

  const tableRef = useRef();

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  // 🔹 Fetch Faculty Load
  const handleViewFacultyLoad = async () => {
    setLoading(true);
    try {
      const res = await API.get("/upload/faculty-load/view");
      setRecords(res.data.data);
      setFacultyList([...new Set(res.data.data.map((r) => r["Faculty Name"]))]);
    } catch (err) {
      alert(err.response?.data?.detail || "Unable to fetch faculty load");
      setRecords([]);
    } finally {
      setLoading(false);
    }
  };

  // 🔹 Fetch Timetable
  const handleViewTimetable = async () => {
    setLoading(true);
    try {
      const res = await API.get("/timetable/list");
      const data = res.data.data || [];

      setTimetable(data);
      setFilteredTimetable(data);

      setSectionList([...new Set(data.map((r) => r.section))]);
      setFacultyList([...new Set(data.map((r) => r.faculty))]);
      setSemesterList([...new Set(data.map((r) => r.year))]); // 🔹 New: semester dropdown
    } catch (err) {
      alert(err.response?.data?.detail || "Unable to fetch timetable");
      setTimetable([]);
      setFilteredTimetable([]);
    } finally {
      setLoading(false);
    }
  };

  // 🔹 Apply filters together
  useEffect(() => {
    let filtered = timetable;

    if (selectedFaculty)
      filtered = filtered.filter((t) => t.faculty === selectedFaculty);
    if (selectedSection)
      filtered = filtered.filter((t) => t.section === selectedSection);
    if (selectedSemester)
      filtered = filtered.filter((t) => String(t.year) === String(selectedSemester));

    setFilteredTimetable(filtered);
  }, [selectedFaculty, selectedSection, selectedSemester, timetable]);

  const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];
  const timeSlots = [
    "9:00–10:00",
    "10:00–11:00",
    "11:00–12:00",
    "12:00–1:00",
    "1:00–2:00",
    "2:00–3:00",
    "3:00–4:00",
  ];

  // 📄 Download PDF
const downloadPDF = async () => {
  const input = tableRef.current;
  const canvas = await html2canvas(input, {
    scale: 6, // ultra sharp text
    useCORS: true,
    backgroundColor: "#ffffff",
    onclone: (doc) => {
      // Fix Tailwind oklch() color parsing issue
      doc.querySelectorAll("*").forEach((el) => {
        const style = getComputedStyle(el);
        if (style.color.includes("oklch")) el.style.color = "black";
        if (style.backgroundColor.includes("oklch"))
          el.style.backgroundColor = "white";
        if (style.borderColor.includes("oklch"))
          el.style.borderColor = "black";
      });
    },
  });

  const imgData = canvas.toDataURL("image/png");
  const pdf = new jsPDF("landscape", "mm", "a4");

  const pageWidth = pdf.internal.pageSize.getWidth();
  const pageHeight = pdf.internal.pageSize.getHeight();

  // Maintain proportion
  const maxWidth = pageWidth - 40;
  const maxHeight = pageHeight - 80;
  let renderWidth = maxWidth;
  let renderHeight = (canvas.height * maxWidth) / canvas.width;
  if (renderHeight > maxHeight) {
    renderHeight = maxHeight;
    renderWidth = (canvas.width * maxHeight) / canvas.height;
  }
  const centerX = (pageWidth - renderWidth) / 2;
  const startY = 60;

  // 🔹 Header Bar
  pdf.setFillColor(59, 130, 246); // Tailwind blue-500
  pdf.rect(0, 0, pageWidth, 25, "F");
  pdf.setTextColor(255, 255, 255);
  pdf.setFont("helvetica", "bold");
  pdf.setFontSize(17);
  pdf.text("EduChrono | Department Timetable", pageWidth / 2, 16, {
    align: "center",
  });

  // 🔹 Subheader Info Box (centered gray)
  pdf.setFont("helvetica", "normal");
  pdf.setFontSize(12);
  pdf.setTextColor(40);
  let infoLine = "Complete Department Timetable";

  if (selectedFaculty) infoLine = `Faculty: ${selectedFaculty}`;
  if (selectedSection) infoLine += `   |   Section: ${selectedSection}`;
  if (selectedSemester) infoLine += `   |   Semester: ${selectedSemester}`;

  pdf.setDrawColor(220);
  pdf.setFillColor(245, 245, 245);
  pdf.rect(10, 30, pageWidth - 20, 20, "F");
  pdf.text(infoLine, pageWidth / 2, 43, { align: "center" });

  // 🧾 Timetable Image (centered perfectly)
  pdf.addImage(imgData, "PNG", centerX, startY, renderWidth, renderHeight);

  // 🔻 Footer
  pdf.setDrawColor(220);
  pdf.line(10, pageHeight - 12, pageWidth - 10, pageHeight - 12);
  pdf.setFontSize(10);
  pdf.setTextColor(100);
  pdf.text("Generated by EduChrono", pageWidth / 2, pageHeight - 6, {
    align: "center",
  });

  pdf.save(
    `Timetable_${selectedFaculty || selectedSection || selectedSemester || "Department"}.pdf`
  );
};



  return (
    <div className="p-8 bg-gray-50 min-h-screen">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-semibold text-blue-700">
          HOD Dashboard – {user?.name}
        </h1>
        <button
          onClick={handleLogout}
          className="bg-red-500 text-white px-4 py-2 rounded-md hover:bg-red-600"
        >
          Logout
        </button>
      </div>

      {/* Faculty Load */}
      <div className="bg-white shadow rounded-xl p-6 mb-8">
        <h2 className="text-lg font-medium mb-4">👩‍🏫 Faculty Workload</h2>
        <button
          onClick={handleViewFacultyLoad}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md"
        >
          View Faculty Load
        </button>

        {loading && <p className="text-gray-500 mt-4">Loading...</p>}

        {!loading && records.length > 0 && (
          <div className="overflow-x-auto mt-6">
            <table className="table-auto w-full border-collapse border border-gray-300 bg-white">
              <thead className="bg-blue-100">
                <tr>
                  {Object.keys(records[0]).map((key) => (
                    <th
                      key={key}
                      className="border border-gray-300 px-4 py-2 text-left text-sm font-semibold text-gray-700"
                    >
                      {key}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {records.map((row, i) => (
                  <tr key={i} className="hover:bg-gray-50">
                    {Object.values(row).map((val, j) => (
                      <td
                        key={j}
                        className="border border-gray-300 px-4 py-2 text-sm text-gray-700"
                      >
                        {val}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Department Timetable */}
      <div className="bg-white shadow rounded-xl p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-medium">📅 Department Timetable</h2>
          {filteredTimetable.length > 0 && (
            <button
              onClick={downloadPDF}
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition"
            >
              📄 Download PDF
            </button>
          )}
        </div>

        <div className="flex flex-wrap gap-4 mb-4">
          <button
            onClick={handleViewTimetable}
            className="bg-green-600 hover:bg-green-700 text-white px-5 py-2 rounded-md"
          >
            Load Timetable
          </button>

          {timetable.length > 0 && (
            <>
              <select
                value={selectedFaculty}
                onChange={(e) => setSelectedFaculty(e.target.value)}
                className="border px-3 py-2 rounded-md text-gray-700"
              >
                <option value="">All Faculty</option>
                {facultyList.map((f, i) => (
                  <option key={i} value={f}>
                    {f}
                  </option>
                ))}
              </select>

              <select
                value={selectedSection}
                onChange={(e) => setSelectedSection(e.target.value)}
                className="border px-3 py-2 rounded-md text-gray-700"
              >
                <option value="">All Sections</option>
                {sectionList.map((s, i) => (
                  <option key={i} value={s}>
                    {s}
                  </option>
                ))}
              </select>

              {/* 🎓 New Semester Filter */}
              <select
                value={selectedSemester}
                onChange={(e) => setSelectedSemester(e.target.value)}
                className="border px-3 py-2 rounded-md text-gray-700"
              >
                <option value="">All Semesters</option>
                {semesterList.map((sem, i) => (
                  <option key={i} value={sem}>
                    Semester {sem}
                  </option>
                ))}
              </select>
            </>
          )}
        </div>

        {loading && <p className="text-gray-500">Loading timetable...</p>}

        {!loading && filteredTimetable.length > 0 && (
          <div ref={tableRef} className="overflow-x-auto mt-6">
            <table className="border-collapse border border-gray-400 w-full text-center">
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
                {days.map((day, dayIndex) => (
                  <tr key={day}>
                    <td className="border border-gray-400 p-2 font-semibold bg-gray-50">
                      {day}
                    </td>

                    {timeSlots.map((slot) => {
                      if (slot === "1:00–2:00") {
                        if (dayIndex === 0) {
                          return (
                            <td
                              key="lunch"
                              rowSpan={days.length}
                              className="border border-gray-400 bg-yellow-100 font-semibold text-gray-800 text-center align-middle"
                            >
                              🍱 LUNCH BREAK
                            </td>
                          );
                        }
                        return null;
                      }

                      // Lab entry
                      const lab = filteredTimetable.find(
                        (t) =>
                          t.day?.toLowerCase() === day.toLowerCase() &&
                          t.type === "P" &&
                          t.time_slot?.startsWith(slot)
                      );
                      const prevLab = filteredTimetable.find(
                        (t) =>
                          t.day?.toLowerCase() === day.toLowerCase() &&
                          t.type === "P" &&
                          t.time_slot?.includes(slot) &&
                          !t.time_slot?.startsWith(slot)
                      );
                      if (prevLab) return null;

                      if (lab) {
                        return (
                          <td
                            key={`${day}-${slot}-lab`}
                            colSpan={2}
                            className="border border-gray-400 bg-green-50 font-semibold text-sm text-gray-800 p-2 whitespace-pre-line"
                          >
                            🧪 {lab.subject}
                            <br />
                            {lab.room}
                            <br />
                            {lab.faculty}
                            <br />
                            Sec {lab.section} | Sem {lab.year}
                          </td>
                        );
                      }

                      // Lecture entry
                      const match = filteredTimetable.find(
                        (t) =>
                          t.day?.toLowerCase() === day.toLowerCase() &&
                          t.time_slot?.toLowerCase() === slot.toLowerCase()
                      );

                      return (
                        <td
                          key={`${day}-${slot}`}
                          className="border border-gray-400 p-2 whitespace-pre-line text-sm text-gray-700"
                        >
                          {match
                            ? `${match.subject}\n${match.faculty}\n${match.room}\nSec ${match.section} | Sem ${match.year}`
                            : "-"}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {!loading && filteredTimetable.length === 0 && (
          <p className="text-gray-500 mt-4">No timetable data available yet.</p>
        )}
      </div>
    </div>
  );
};

export default DashboardHOD;
