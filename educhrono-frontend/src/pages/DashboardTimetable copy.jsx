import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import FileUploader from "../components/FileUploader";
import API from "../services/api";
import html2canvas from "html2canvas";
import jsPDF from "jspdf";

export default function DashboardTimetable() {
  const [uploading, setUploading] = useState(false);
  const [loadingView, setLoadingView] = useState(false);
  const [viewType, setViewType] = useState("");
  const [records, setRecords] = useState([]);
  const [timetable, setTimetable] = useState([]);
  const [filteredTimetable, setFilteredTimetable] = useState([]);
  const [facultyList, setFacultyList] = useState([]);
  const [sectionList, setSectionList] = useState([]);
  const [semesterList, setSemesterList] = useState([]);
  const [selectedFaculty, setSelectedFaculty] = useState("");
  const [selectedSection, setSelectedSection] = useState("");
  const [selectedSemester, setSelectedSemester] = useState("");
  const [role, setRole] = useState("");
  const [user, setUser] = useState(null);
  const tableRef = useRef();

  const navigate = useNavigate();

  // 🧩 AUTH CHECK
  useEffect(() => {
    const u = JSON.parse(localStorage.getItem("edu_user"));
    if (u?.role) {
      setRole(u.role.toUpperCase());
      setUser(u);
    } else navigate("/login");
  }, [navigate]);

  // 🔹 Logout
  const handleLogout = () => {
    localStorage.removeItem("edu_user");
    navigate("/login");
  };

  // 🔹 Upload Excel
  const handleUpload = async (file, type) => {
    const formData = new FormData();
    formData.append("file", file);
    setUploading(true);
    try {
      const res = await API.post(`/upload/${type}`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      alert(res.data.message);
    } catch (err) {
      alert(err.response?.data?.detail || "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  // 🔹 View Uploaded Data
  const handleView = async (type) => {
    setLoadingView(true);
    setViewType(type);
    try {
      const res = await API.get(`/upload/${type}/view`);
      setRecords(res.data.data);
    } catch (err) {
      alert(err.response?.data?.detail || "No data found");
      setRecords([]);
    } finally {
      setLoadingView(false);
    }
  };

  // 🔹 Generate Timetable
  const handleGenerate = async () => {
    try {
      const res = await API.post("/timetable/generate");
      alert(res.data.message || "Timetable generated successfully.");
    } catch (err) {
      alert(err.response?.data?.detail || "Generation failed");
    }
  };

  // 🔹 View Generated Timetable
  const handleViewTimetable = async () => {
    setLoadingView(true);
    setViewType("timetable");
    try {
      const res = await API.get("/timetable/list");
      let data = res.data.data || [];

      // Normalize and remove (B1/B2)
      data = data.map((i) => ({
        ...i,
        faculty: i.faculty?.trim(),
        section: i.section
          ?.trim()
          .toUpperCase()
          .replace(/\s*\(B\d\)/gi, ""),
        day: i.day?.trim(),
        time_slot: i.time_slot?.trim(),
      }));

      setTimetable(data);
      setFilteredTimetable(data);
      setFacultyList([...new Set(data.map((i) => i.faculty).filter(Boolean))]);
      setSectionList([...new Set(data.map((i) => i.section).filter(Boolean))]);
      setSemesterList([...new Set(data.map((i) => i.year).filter(Boolean))]);
      setSelectedFaculty("");
      setSelectedSection("");
      setSelectedSemester("");
    } catch (err) {
      alert(err.response?.data?.detail || "No timetable found");
      setTimetable([]);
      setFilteredTimetable([]);
    } finally {
      setLoadingView(false);
    }
  };

  // 🔹 Auto Filter
  useEffect(() => {
    let filtered = timetable;
    if (selectedFaculty)
      filtered = filtered.filter(
        (t) =>
          t.faculty?.trim().toUpperCase() ===
          selectedFaculty.trim().toUpperCase()
      );
    if (selectedSection)
      filtered = filtered.filter(
        (t) =>
          t.section?.trim().toUpperCase() ===
          selectedSection.trim().toUpperCase()
      );
    if (selectedSemester)
      filtered = filtered.filter(
        (t) => String(t.year) === String(selectedSemester)
      );
    setFilteredTimetable(filtered);
  }, [selectedFaculty, selectedSection, selectedSemester, timetable]);

  // 🔹 Template Download
  const handleDownloadTemplate = (type) =>
    window.open(`http://localhost:8000/upload/template/${type}`, "_blank");

  const downloadPDF = async () => {
    const input = tableRef.current;
    if (!input) return;

    // Clone timetable node
    const clone = input.cloneNode(true);
    document.body.appendChild(clone);
    clone.style.position = "absolute";
    clone.style.left = "-9999px";
    clone.style.background = "#ffffff";

    // ✅ Sanitize OKLCH / LAB colors (replace with RGB)
    const sanitizeColors = (el) => {
      const computedStyle = window.getComputedStyle(el);
      for (const prop of ["color", "backgroundColor", "borderColor"]) {
        const val = computedStyle[prop];
        if (val && val.includes("oklch")) {
          // Replace any OKLCH-based color with neutral RGB
          el.style[prop] = "#f8fafc"; // Tailwind neutral background
        }
      }
      for (const child of el.children) sanitizeColors(child);
    };
    sanitizeColors(clone);

    // ✅ Inject fallback CSS to avoid re-triggering Tailwind dynamic colors
    const style = document.createElement("style");
    style.innerHTML = `
    * {
      font-family: 'Inter', sans-serif !important;
      color: #111827 !important;
    }
    table { border-collapse: collapse !important; width: 100% !important; }
    th, td {
      border: 1px solid #000 !important;
      text-align: center !important;
      padding: 6px !important;
    }
    th { background: rgb(219, 234, 254) !important; }
    td:first-child { background: rgb(224, 242, 254) !important; font-weight: 600 !important; }
    tr:nth-child(even) td:not(:first-child) { background: rgb(236, 253, 245) !important; }
    .lunch-cell { background: rgb(255, 247, 204) !important; font-weight: bold !important; }
  `;
    clone.prepend(style);

    try {
      const canvas = await html2canvas(clone, {
        scale: 3,
        backgroundColor: "#ffffff",
        logging: false,
        useCORS: true,
      });

      document.body.removeChild(clone);

      const pdf = new jsPDF("landscape", "mm", "a4");
      const pageWidth = pdf.internal.pageSize.getWidth();
      const pageHeight = pdf.internal.pageSize.getHeight();

      const imgData = canvas.toDataURL("image/png");
      const aspectRatio = canvas.width / canvas.height;
      let imgWidth = pageWidth - 10;
      let imgHeight = imgWidth / aspectRatio;
      if (imgHeight > pageHeight - 45) {
        imgHeight = pageHeight - 45;
        imgWidth = imgHeight * aspectRatio;
      }

      const x = (pageWidth - imgWidth) / 2;
      const y = 45;

      pdf.setFont("helvetica", "bold");
      pdf.setFontSize(14);
      pdf.text(
        "MORADABAD INSTITUTE OF TECHNOLOGY, MORADABAD",
        pageWidth / 2,
        15,
        { align: "center" }
      );
      pdf.setFont("helvetica", "normal");
      pdf.setFontSize(12);
      pdf.text(
        "Department of Computer Science & Engineering - Timetable",
        pageWidth / 2,
        22,
        { align: "center" }
      );

      const studentName = user?.name || "Student";
      const sem = semester || "N/A";
      const sec = section || "N/A";
      const academicYear = "2025–26";

      pdf.setFontSize(11);
      pdf.text(
        `Student: ${studentName}   |   Semester: ${sem}   |   Section: ${sec}   |   Academic Year: ${academicYear}`,
        pageWidth / 2,
        30,
        { align: "center" }
      );

      pdf.addImage(imgData, "PNG", x, y, imgWidth, imgHeight);
      const date = new Date().toLocaleDateString("en-IN", {
        day: "2-digit",
        month: "short",
        year: "numeric",
      });
      pdf.setFontSize(10);
      pdf.setTextColor(90);
      pdf.text(
        `Generated by EduChrono on ${date}`,
        pageWidth / 2,
        pageHeight - 8,
        { align: "center" }
      );

      pdf.save(`Timetable_${studentName}.pdf`);
    } catch (err) {
      console.error("PDF Error:", err);
      alert("Error generating PDF.");
    }
  };

  const days = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
  ];
  const timeSlots = [
    "9:00–10:00",
    "10:00–11:00",
    "11:00–12:00",
    "12:00–1:00",
    "1:00–2:00",
    "2:00–3:00",
    "3:00–4:00",
  ];

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <h2 className="text-3xl font-bold text-blue-700">
          📘 EduChrono | Timetable Dashboard ({role})
        </h2>
        <button
          onClick={handleLogout}
          className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-md shadow-sm"
        >
          Logout
        </button>
      </div>

      {/* ========================== ADMIN / HOD ========================== */}
      {["ADMIN", "HOD"].includes(role) && (
        <>
          {/* Upload Section */}
          <section className="bg-white p-6 rounded-xl shadow-md mb-10">
            <h3 className="text-xl font-semibold text-gray-700 mb-4">
              ⬆️ Upload Excel Data
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <FileUploader
                label="Upload Faculty Load"
                onUpload={(f) => handleUpload(f, "faculty-load")}
                onDownloadTemplate={() =>
                  handleDownloadTemplate("faculty-load")
                }
              />
              <FileUploader
                label="Upload Teaching Load"
                onUpload={(f) => handleUpload(f, "teaching-load")}
                onDownloadTemplate={() =>
                  handleDownloadTemplate("teaching-load")
                }
              />
              {role === "ADMIN" && (
                <>
                  <FileUploader
                    label="Upload Room List"
                    onUpload={(f) => handleUpload(f, "room-list")}
                    onDownloadTemplate={() =>
                      handleDownloadTemplate("room-list")
                    }
                  />
                  <FileUploader
                    label="Upload Lab List"
                    onUpload={(f) => handleUpload(f, "lab-list")}
                    onDownloadTemplate={() =>
                      handleDownloadTemplate("lab-list")
                    }
                  />
                </>
              )}
            </div>
            {uploading && (
              <p className="mt-4 text-blue-500 font-medium">
                Uploading... please wait
              </p>
            )}
          </section>
          {/* View Uploaded Data */}
          <section className="bg-white p-6 rounded-xl shadow-md mb-10">
            <h3 className="text-xl font-semibold text-gray-700 mb-4">
              👁️ View Uploaded Data
            </h3>
            <div className="flex flex-wrap gap-4 mb-6">
              <button
                onClick={() => handleView("faculty-load")}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md"
              >
                View Faculty Load
              </button>
              <button
                onClick={() => handleView("teaching-load")}
                className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-md"
              >
                View Teaching Load
              </button>
              <button
                onClick={() => handleView("room-list")}
                className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md"
              >
                View Room List
              </button>
              <button
                onClick={() => handleView("lab-list")}
                className="bg-orange-600 hover:bg-orange-700 text-white px-4 py-2 rounded-md"
              >
                View Lab List
              </button>
            </div>

            {loadingView && <p className="text-gray-500">Loading data...</p>}
            {!loadingView && records.length > 0 && (
              <div className="overflow-x-auto mt-4">
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
          </section>
          {/* Generate & View */}
          <section className="bg-white p-6 rounded-xl shadow-md">
            <h3 className="text-xl font-semibold text-gray-700 mb-4">
              🧮 Generate & View Timetable
            </h3>
            <div className="flex flex-wrap gap-4 mb-6">
              {role === "ADMIN" && (
                <button
                  onClick={handleGenerate}
                  className="bg-green-600 hover:bg-green-700 text-white px-5 py-2 rounded-md"
                >
                  Generate Timetable
                </button>
              )}
              <button
                onClick={handleViewTimetable}
                className="bg-blue-700 hover:bg-blue-800 text-white px-5 py-2 rounded-md"
              >
                View Generated Timetable
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

            {/* Timetable */}
            {!loadingView && filteredTimetable.length > 0 && (
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

                        {timeSlots.map((slot, slotIndex) => {
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

                          // 🧩 Find a lab that starts here
                          const lab = filteredTimetable.find(
                            (t) =>
                              t.day?.toLowerCase() === day.toLowerCase() &&
                              t.type === "P" &&
                              t.time_slot?.startsWith(slot)
                          );

                          // 🧩 Handle 2-hour labs (example: 9:00–11:00 or 2:00–4:00)
                          if (lab) {
                            const subj = lab.subject;
                            const mergedRooms = filteredTimetable
                              .filter(
                                (l) =>
                                  l.day?.toLowerCase() === day.toLowerCase() &&
                                  l.subject === subj &&
                                  l.time_slot === lab.time_slot
                              )
                              .map(
                                (l) =>
                                  `${l.room}${l.batch ? ` (${l.batch})` : ""}`
                              )
                              .join(" | ");

                            // Determine if lab spans 2 hours
                            const duration =
                              lab.time_slot.includes("–11:00") ||
                              lab.time_slot.includes("–4:00") ||
                              lab.time_slot.includes("–1:00")
                                ? 2
                                : 1;

                            return (
                              <td
                                key={`${day}-${slot}-lab`}
                                colSpan={duration}
                                className="border border-gray-400 bg-green-50 font-semibold text-sm text-gray-800 p-2 whitespace-pre-line"
                              >
                                🧪 {subj}
                                <br />
                                {mergedRooms}
                                <br />
                                {lab.faculty}
                                <br />
                                Sec {lab.section} | Sem {lab.year}
                              </td>
                            );
                          }

                          // 🧩 If this slot is already covered by a 2-hour lab, skip
                          const overlappingLab = filteredTimetable.find(
                            (t) =>
                              t.day?.toLowerCase() === day.toLowerCase() &&
                              t.type === "P" &&
                              t.time_slot?.includes(slot) &&
                              !t.time_slot?.startsWith(slot)
                          );
                          if (overlappingLab) return null;

                          // 🧩 Theory Subjects
                          // 🧩 Theory / Tutorial / Lab (Single-Slot)
                          const slotEntries = filteredTimetable.filter(
                            (t) =>
                              t.day?.toLowerCase() === day.toLowerCase() &&
                              t.time_slot?.toLowerCase() === slot.toLowerCase()
                          );

                          if (slotEntries.length === 0) {
                            return (
                              <td
                                key={`${day}-${slot}`}
                                className="border border-gray-400 p-2 text-sm text-gray-700"
                              >
                                -
                              </td>
                            );
                          }

                          // Split static B1/B2 for tutorials and practicals
                          let finalEntries = [];
                          slotEntries.forEach((e) => {
                            if (e.type === "P" || e.type === "T") {
                              // Create two batches visually if both exist
                              if (e.batch) {
                                finalEntries.push(e);
                              } else {
                                finalEntries.push({ ...e, batch: "B1" });
                                finalEntries.push({ ...e, batch: "B2" });
                              }
                            } else {
                              finalEntries.push(e);
                            }
                          });

                          return (
                            <td
                              key={`${day}-${slot}`}
                              className="border border-gray-400 p-2 whitespace-pre-line text-sm font-medium text-gray-800"
                            >
                              {finalEntries.map((entry, idx) => (
                                <div
                                  key={idx}
                                  className="mb-1 border-b border-gray-300 pb-1 last:border-0"
                                >
                                  <span className="block font-semibold text-gray-900">
                                    {entry.subject_code || entry.subject} (
                                    {entry.type}
                                    {entry.batch ? ` - ${entry.batch}` : ""})
                                  </span>
                                  <span className="block text-gray-700">
                                    {entry.faculty}
                                  </span>
                                  <span className="block text-gray-600">
                                    {entry.room}
                                  </span>
                                  <span className="block text-gray-500">
                                    Sec {entry.section} | Sem {entry.year}
                                  </span>
                                </div>
                              ))}
                            </td>
                          );
                        })}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {filteredTimetable.length > 0 && (
              <div className="text-right mt-4">
                <button
                  onClick={downloadPDF}
                  className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
                >
                  📄 Download PDF
                </button>
              </div>
            )}
          </section>
        </>
      )}
    </div>
  );
}
