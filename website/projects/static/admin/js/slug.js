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

        const existing_repo_names = existingrepositoryFieldset.querySelectorAll(
            '[id^="id_existingrepository_set-"][id$="-name"]'
        );

        const repo_names = document.querySelectorAll(
            '[id^="id_newrepository_set-"][id$="-name"]'
        );
        
        if(checked && slug.value != ""){
            for(const repo_name of repo_names){
                if(repo_name.value == slug.value){
                    invalid.push(repo_name);
                }
            }
        }
        
        for(const repo_name of existing_repo_names){
            if(!names.includes(repo_name.value)){
                names.push(repo_name.value);
            }
            else{
                if(!invalid.includes(repo_name) && repo_name.value != ""){
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
        const repo_names = document.querySelectorAll('[id^="id_newrepository_set-"][id$="-name"]');
        const existing_repo_names = document.querySelectorAll('[id^="id_existingrepository_set-"][id$="-name"]');

        for(const repo_name of repo_names){
            repo_name.style.border = "";
        }

        for(const repo_name of existing_repo_names){
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

    const newrepositoryFieldset = document.querySelector(
        "#newrepository_set-group"
    );

    if (newrepositoryFieldset) {
        newrepositoryFieldset.addEventListener("input", repoErrorUpdate);
    }
    default_repo.addEventListener("change", repoErrorUpdate);

    const existingrepositoryFieldset = document.querySelector(
        "#existingrepository_set-group"
    );

    document.addEventListener("click", addLinkListener);
    function addLinkListener(){
        const addlink1 = newrepositoryFieldset.querySelector(".addlink");
        const addlink2 = existingrepositoryFieldset.querySelector(".addlink");
        if(addlink1){
            addlink1.addEventListener("click", createRemoveListeners);
            document.removeEventListener("click", addLinkListener);
            fetchTimeout();
        }
        if(addlink2){
            addlink2.addEventListener("click", fetchTimeout);
            document.removeEventListener("click", addLinkListener);
            fetchTimeout();
        }
    }
    function createRemoveListeners(){
        const remove_buttons = newrepositoryFieldset.querySelectorAll(".inline-deletelink");

        for(const remove_button of remove_buttons){
            remove_button.removeEventListener("click", repoErrorUpdate);
            remove_button.addEventListener("click", repoErrorUpdate);
        }
    }

    function fetchTimeout(){
        const repo_names = existingrepositoryFieldset.querySelectorAll(
            '[id^="id_existingrepository_set-"][id$="-name"]'
        );

        const repo_ids = existingrepositoryFieldset.querySelectorAll(
            '[id^="id_existingrepository_set-"][id$="-github_repo_id"]'
        );

        const remove_buttons = existingrepositoryFieldset.querySelectorAll(".inline-deletelink");

        for(const repo_name of repo_names){
            repo_name.removeEventListener("click", repoErrorUpdate);
            repo_name.addEventListener("click", repoErrorUpdate);
        }

        for(const repo_id of repo_ids){
            let timeout = null;
            repo_id.removeEventListener("keyup", keyUp);
            repo_id.addEventListener("keyup", keyUp);
        }

        for(const remove_button of remove_buttons){
            remove_button.removeEventListener("click", repoErrorUpdate)
            remove_button.addEventListener("click", repoErrorUpdate)
        }

        disableFields();
    }

    function disableFields(){
        const nameFields = existingrepositoryFieldset.querySelectorAll("input[name$='name']");

        for(const name of nameFields){
            const row = name.closest(".inline-related");
            const private = row.querySelector("input[name$='private']");
            const archived = row.querySelector("select[name$='is_archived']");
            const repo_id = row.querySelector('input[name$="github_repo_id"]');

            if(!repo_id.disabled){
                name.disabled = true;
                private.disabled = true;
                archived.disabled = true;
            }
        }
    }

    const keyUp = (e) => {
        clearTimeout(e.target._timeout);

        e.target._timeout = setTimeout(() => {
            fetchData(e);
        }, 500);
    };

    async function fetchData(e){
        const url = `/admin/projects/project/fetch-repo/?github_repo_id=${encodeURIComponent(e.target.value)}`;
        const row = e.target.closest(".inline-related");

        try {
            const res = await fetch(url);
            const data = await res.json();

            if (data.error) {
                e.target.style.border = "1px solid #e35f5f";
                document.getElementById("error" + e.target.id)?.remove();
                const parent = e.target.closest(".form-row.field-github_repo_id");
                const error = createErrorMessage(data.error);
                error.id = "error" + e.target.id;
                parent.before(error);
                return;
            }
            e.target.style.border = "";
            document.getElementById("error" + e.target.id)?.remove();
            e.target.disabled = true;

            const nameField = row.querySelector("input[name$='name']");
            nameField.disabled = false;
            const privateField = row.querySelector("input[name$='private']");
            privateField.disabled = false;
            const archivedField = row.querySelector("select[name$='is_archived']");
            archivedField.disabled = false;

            if (nameField) nameField.value = data.name;
            if (privateField) privateField.checked = data.private;
            if (archivedField) {
            archivedField.value = String(data.archived);

            archivedField.dispatchEvent(new Event("change", { bubbles: true }));
            }
            repoErrorUpdate();
        } catch (err) {
            document.getElementById("error" + e.target.id)?.remove();
            e.target.style.border = "1px solid #e35f5f";
            const parent = e.target.closest(".form-row.field-github_repo_id");
            const error = createErrorMessage("Fetch failed");
            error.id = "error" + e.target.id;
            parent.before(error);
        }
    }

    save.addEventListener('mouseenter', () => {
        const nameFields = existingrepositoryFieldset.querySelectorAll("input[name$='name']");
        const privateFields = existingrepositoryFieldset.querySelectorAll("input[name$='private']");
        const archivedFields = existingrepositoryFieldset.querySelectorAll("select[name$='is_archived']");
        const repo_ids = existingrepositoryFieldset.querySelectorAll(
            '[id^="id_existingrepository_set-"][id$="-github_repo_id"]'
        );

        disable(nameFields);
        disable(privateFields);
        disable(archivedFields);
        disable(repo_ids);
    });

    function disable(list){
        for(item of list){
            item.disabled = false;
        }
    }

    save.addEventListener('mouseleave', () => {
        disableFields();
    });

});