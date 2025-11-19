import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import FileUploader from "../components/FileUploader";
import API from "../services/api";
import html2canvas from "html2canvas";
import jsPDF from "jspdf";
import TimetableTable from "../components/TimetableTable";

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
          t.faculty?.toLowerCase().trim() ===
          selectedFaculty.toLowerCase().trim()
      );

    if (selectedSection)
      filtered = filtered.filter(
        (t) =>
          t.section?.replace(/\s+/g, "").toUpperCase() ===
          selectedSection.replace(/\s+/g, "").toUpperCase()
      );

    if (selectedSemester)
      filtered = filtered.filter(
        (t) =>
          String(t.year).replace(/\D/g, "") ===
          String(selectedSemester).replace(/\D/g, "")
      );

    setFilteredTimetable(filtered);
  }, [selectedFaculty, selectedSection, selectedSemester, timetable]);


  // 🔹 Template Download
  const handleDownloadTemplate = (type) =>
    window.open(`http://localhost:8000/upload/template/${type}`, "_blank");


// 📄 Download Department Timetable as PDF (Admin/HOD)
const downloadPDF = async () => {
  const input = tableRef.current;
  if (!input) {
    alert("No timetable to export");
    return;
  }

  // Clone the table for a clean snapshot
  const clone = input.cloneNode(true);
  document.body.appendChild(clone);
  clone.style.position = "absolute";
  clone.style.left = "-9999px";
  clone.style.background = "#ffffff";

  // 🧩 Sanitize Tailwind oklch() colors (same as Student logic)
  const sanitizeColors = (el) => {
    const computed = window.getComputedStyle(el);
    for (const prop of ["color", "backgroundColor", "borderColor"]) {
      const val = computed[prop];
      if (val && val.includes("oklch")) el.style[prop] = "#f8fafc";
    }
    for (const child of el.children) sanitizeColors(child);
  };
  sanitizeColors(clone);

  // ✅ Force table style consistency
  const style = document.createElement("style");
  style.innerHTML = `
    * { font-family: 'Inter', sans-serif !important; color: #111827 !important; }
    table { border-collapse: collapse !important; width: 100% !important; }
    th, td { border: 1px solid #000 !important; padding: 6px !important; text-align: center !important; }
    th { background: rgb(219,234,254) !important; }
    td:first-child { background: rgb(224,242,254) !important; font-weight: 600 !important; }
    .lunch-cell { background: rgb(255,247,204) !important; font-weight: bold !important; }
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

    // 🧾 Prepare PDF layout
    const pdf = new jsPDF("landscape", "mm", "a4");
    const pageWidth = pdf.internal.pageSize.getWidth();
    const pageHeight = pdf.internal.pageSize.getHeight();
    const imgData = canvas.toDataURL("image/png");
    const aspectRatio = canvas.width / canvas.height;

    // 🧩 Fit 9–5 PM table nicely
    let imgWidth = pageWidth - 20; // slightly narrower for margins
    let imgHeight = imgWidth / aspectRatio;
    if (imgHeight > pageHeight - 60) {
      imgHeight = pageHeight - 60;
      imgWidth = imgHeight * aspectRatio;
    }

    const x = (pageWidth - imgWidth) / 2;
    const y = 40;

    // 🏫 Header
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
      "Department of Computer Science & Engineering – Consolidated Timetable (9:00 AM – 5:00 PM)",
      pageWidth / 2,
      22,
      { align: "center" }
    );

    const name = user?.name || "Admin/HOD";
    const academicYear = "2025–26";
    const sem = selectedSemester || "All";
    const sec = selectedSection || "All";
    const faculty = selectedFaculty || "All";

    pdf.setFontSize(11);
    pdf.text(
      `Generated by: ${name} | Semester: ${sem} | Section: ${sec} | Faculty: ${faculty} | Academic Year: ${academicYear}`,
      pageWidth / 2,
      30,
      { align: "center" }
    );

    // 🧩 Add timetable image
    pdf.addImage(imgData, "PNG", x, y, imgWidth, imgHeight);

    const date = new Date().toLocaleDateString("en-IN", {
      day: "2-digit",
      month: "short",
      year: "numeric",
    });

    // 📅 Footer
    pdf.setFont("helvetica", "normal");
    pdf.setFontSize(10);
    pdf.setTextColor(80);

    let footerY = y + imgHeight + 25;
    if (footerY > pageHeight - 25) {
      pdf.addPage();
      footerY = 25;
    }

    // Divider line
    pdf.setDrawColor(150);
    pdf.setLineWidth(0.3);
    pdf.line(15, footerY - 10, pageWidth - 15, footerY - 10);

    // 🖋️ Signature Section (Neat Alignment)
    const leftX = 35;
    const rightX = pageWidth - 105;
    const lineY = footerY - 4;

    // Optional signature lines
    pdf.setDrawColor(0);
    pdf.line(leftX, lineY, leftX + 60, lineY);
    pdf.line(rightX, lineY, rightX + 60, lineY);

    pdf.setFont("helvetica", "bold");
    pdf.setFontSize(11);
    pdf.text("(Ms. Neha Gupta)", leftX + 5, footerY + 4);
    pdf.setFont("helvetica", "normal");
    pdf.setFontSize(10);
    pdf.text("Dept. Coordinator (Timetable)", leftX + 5, footerY + 12);

    pdf.setFont("helvetica", "bold");
    pdf.setFontSize(11);
    pdf.text("(Dr. Lalit Mohan Trivedi)", rightX + 5, footerY + 4);
    pdf.setFont("helvetica", "normal");
    pdf.setFontSize(10);
    pdf.text("Convener (Timetable)", rightX + 5, footerY + 12);


    // 🕒 Generation info
    pdf.setFontSize(9);
    pdf.setTextColor(90);
    pdf.text(
      `Generated by EduChrono on ${date}`,
      pageWidth / 2,
      pageHeight - 10,
      { align: "center" }
    );

    // 💾 Save
    pdf.save(`EduChrono_Timetable_${name}.pdf`);
  } catch (err) {
    console.error("PDF Error:", err);
    alert("Error generating PDF.");
  }
};


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
              <TimetableTable
                timetable={filteredTimetable}
                days={["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]}
                timeSlots={[
                  "9:00–10:00",
                  "10:00–11:00",
                  "11:00–12:00",
                  "12:00–1:00",
                  "1:00–2:00",  // lunch break
                  "2:00–3:00",
                  "3:00–4:00",
                  "4:00–5:00",
                ]}
              />
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
