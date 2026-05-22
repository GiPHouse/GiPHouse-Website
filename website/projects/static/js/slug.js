document.addEventListener("DOMContentLoaded", () => {
    const name = document.getElementById("id_name");
    const semester = document.getElementById("id_semester");
    const slug = document.getElementById("id_slug")
    const repoName = document.getElementById("id_repository_set-0-name")
    var defrepo = document.getElementById("id_default_repo")
    var saveButton = document.getElementsByName("_save")
    
    

    if (!name || !semester || !slug || !repoName) {
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

    
    

    // function uniqueRepo() {
    // //     // als def repo == true, dan als een van repo zelfde naam als slug, throw console.error();
    // //     //saveButton.disabled = true;
    // //     //window.alert("TESTTEST");
    // //     if (!saveButton) {
    // //         window.alert("No button :(");
    // //     } else if (saveButton) {
    // //         window.alert("Yes Button! :)");
    // //         console.log("YOHO OVER HERE");
    // //         console.log(saveButton);
    // //         saveButton.disabled = true;
    // //         console.log("AFter");
    // //         console.log(saveButton);
    // //     } else {
    // //         window.alert("WTF IS GOIN ON");
    // //     }
    // //     if (defrepo && repoName.value == slug.value) {
    // //         saveButton.disabled = true;
    // //         window.alert("Can't add a new repo with slug as name when default repo is checked.");
    // //         //return false;
    // //     } else {
    // //         saveButton.disabled = false;
    // //     }
    //     console.log(defrepo.value);
    //     console.log(defrepo.value == "on");

    //     if (defrepo.value == "on") {
    //         console.log("YOLO");
    //         repoName.value = slug.value;
    //         repoName.readOnly = true;
    //     } else {
    //         repoName.value = slug.value;
    //         repoName.readOnly = false;
    //         //repoName.value = "";
    //     }
    // }

    // defrepo.addEventListener("input", uniqueRepo);
    // // repoName.addEventListener("input", uniqueRepo);
    // // saveButton.addEventListener("input", function(e) {
    // //     e.preventDefault();
    // // });


    // uniqueRepo();
});