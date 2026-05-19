document.addEventListener("DOMContentLoaded", () => {
    const name = document.getElementById("id_name");
    const semester = document.getElementById("id_semester");
    const slug = document.getElementById("id_slug");
    const default_repo = document.getElementById("id_default_repo");
    const save = document.querySelector('[name="_save"]');
    const end_body = document.getElementById("django-admin-form-add-constants")
    var count_invalid = 0;

    if (!name || !semester || !slug) {
        return;
    }

    slug.readOnly = true;

    function slugify(text) {
        return text
            .toLowerCase()
            .replace(/[^\w\s-]/g, "")
            .replace(/[-\s]+/g, "-")
            .replace(/^[-_]+|[-_]+$/g, "");
    }

    function updateSlug() {
        const nameValue = name.value || "";
        var semesterText =
            semester.options[semester.selectedIndex]?.text.slice(-4) || "";

        if (semesterText == "----"){
            semesterText = "";
        }

        slug.value = slugify(`${nameValue}-${semesterText}`);
    }

    name.addEventListener("input", updateSlug);
    semester.addEventListener("input", updateSlug);

    updateSlug();

    const repositoryFieldset = document.querySelector(
        "#repository_set-group"
    );

    if (repositoryFieldset) {
        repositoryFieldset.addEventListener("input", (event) => {
            const target = event.target;

            if (!(target instanceof HTMLInputElement)) {
                return;
            }

            if(default_repo.checked && target.value == slug.value){
                count_invalid++;
                save.disabled = true;
                
                if(count_invalid == 1){
                    target.style.border = "1px solid var(--error-fg)";
                    const error = document.createElement("ul");
                    error.className = "errorlist";
                    error.id = "default_repo_copy";
                    const li = document.createElement("li");
                    li.textContent = "Naming a repo the same as the slug is not allowed when default repo is enabled.";
                    error.appendChild(li);
                    end_body.before(error);
                }
            }
            else{
                target.style.border = "";
                count_invalid--;
                if(count_invalid == 0){
                    save.disabled = false;
                    document.querySelector("#default_repo_copy")?.remove();
                }
            }
        });
    }
});