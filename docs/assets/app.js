async function main() {
  const res = await fetch("manifest.json");
  const data = await res.json();
  const items = data.map(x => ({
    name: x.name,
    url: "people/" + (x.file || "").split("/").pop()
  })).filter(x => x.name && x.url);

  const list = document.getElementById("list");
  const q = document.getElementById("q");
  const count = document.getElementById("count");

  function render(filterText = "") {
    const t = filterText.trim().toLowerCase();
    const filtered = t ? items.filter(i => i.name.toLowerCase().includes(t)) : items;
    count.textContent = `共 ${filtered.length} 条`;
    list.innerHTML = "";
    for (const i of filtered) {
      const li = document.createElement("li");
      const a = document.createElement("a");
      a.href = i.url;
      a.textContent = i.name;
      a.target = "_blank";
      a.rel = "noopener";
      li.appendChild(a);
      list.appendChild(li);
    }
  }

  q.addEventListener("input", () => render(q.value));
  render();
}
main().catch(console.error);
