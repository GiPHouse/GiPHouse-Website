document.addEventListener("DOMContentLoaded", () => {
    const name = document.getElementById("id_name");
    const semester = document.getElementById("id_semester");
    const slug = document.getElementById("id_slug");
    const default_repo = document.getElementById("id_default_repo");
    const default_repo_div = document.querySelector(".field-default_repo")
    const save = document.querySelector('[name="_save"]');
    const end_body = document.getElementById("django-admin-form-add-constants")
    const path = window.location.pathname;

    if (path.endsWith("/change/")) {
        default_repo_div.style.display = "none"
    }
    
    if (!name || !semester || !slug) {
        return;
    }

    slug.disabled = true;

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

    name.addEventListener("input", update);
    semester.addEventListener("input", update);

    updateSlug();

    function invalidRepoNames(checked){
        const invalid = [];
        const names = [];

        const repo_names = document.querySelectorAll(
            '[id^="id_repository_set-"][id$="-name"]'
        );
        
        if(checked && slug.value != ""){
            for(const repo_name of repo_names){
                if(repo_name.value == slug.value){
                    invalid.push(repo_name);
                }
            }
        }

        for(const repo_name of repo_names){
            if(!names.includes(repo_name.value)){
                names.push(repo_name.value);
            }
            else{
                if(!invalid.includes(repo_name) && repo_name.value != ""){
                    invalid.push(repo_name);
                }
            }
        }
        return invalid;
    }

    function repoErrorUpdate(){
        const invalid_repo_names = invalidRepoNames(default_repo.checked);

        if(invalid_repo_names.length > 0){
            save.disabled = true;
            clear();

            if(!document.getElementById("default_repo_copy")){
                const error = createErrorMessage("Naming a repo the same as the slug is not allowed when default repo is enabled.");
                error.id = "default_repo_copy";
                end_body.before(error);
            }

            for(const repo_name of invalid_repo_names){
                repo_name.style.border = "1px solid #e35f5f";
                const parent = repo_name.closest(".form-row.field-name");
                const error = createErrorMessage("Repo name already taken");
                error.classList.add("repo-error");
                parent.before(error);
            }
        }
        else{
            clear();
            save.disabled = false;
            document.querySelector("#default_repo_copy")?.remove();
        }
    }

    function createErrorMessage(message){
        const error = document.createElement("ul");
        error.className = "errorlist";
        const li = document.createElement("li");
        li.textContent = message;
        error.appendChild(li);

        return error;
    }

    function clear(){
        const repo_names = document.querySelectorAll('[id^="id_repository_set-"][id$="-name"]');

        for(const repo_name of repo_names){
            repo_name.style.border = "";
        }

        const error_messages = document.querySelectorAll(".repo-error");

        for(const error_message of error_messages){
            error_message.remove();
        }
    }

    function update(){
        updateSlug();
        repoErrorUpdate();
    }

    const repositoryFieldset = document.querySelector(
        "#repository_set-group"
    );

    if (repositoryFieldset) {
        repositoryFieldset.addEventListener("input", repoErrorUpdate);
    }
    default_repo.addEventListener("change", repoErrorUpdate);
});