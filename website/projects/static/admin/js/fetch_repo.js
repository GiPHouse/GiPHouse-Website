document.addEventListener("click", async function (e) {
    const btn = e.target.closest(".fetch-repo");
    if (!btn) return;

    const row = btn.closest(".inline-related");

    const repoInput = row.querySelector(".github_repo_id-field");
    const repoId = repoInput?.value;

    if (!repoId) {
        alert("Field github_repo_id is empty");
        return;
    }

    const url = `/admin/projects/project/fetch-repo/?github_repo_id=${encodeURIComponent(repoId)}`;

    try {
        const res = await fetch(url);
        const data = await res.json();

        if (data.error) {
            alert(data.error);
            return;
        }

        // fill fields (row-scoped only)
        const nameField = row.querySelector("input[name$='name']");
        const privateField = row.querySelector("input[name$='private']");
        const archivedField = row.querySelector("select[name$='is_archived']");

        if (nameField) nameField.value = data.name;
        if (privateField) privateField.checked = data.private;
        if (archivedField) {
          archivedField.value = String(data.archived);

          archivedField.dispatchEvent(new Event("change", { bubbles: true }));
        }
    } catch (err) {
        alert("Fetch failed");
    }
});
