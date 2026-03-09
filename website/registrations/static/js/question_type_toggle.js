document.addEventListener("DOMContentLoaded", () => {
    function getChoiceCount(questionTbody) {
        const choiceRows = questionTbody.querySelectorAll(
            "tbody[id*='-choices-']:not([id*='empty']) tr.djn-tr.form-row"
        );

        let count = 0;
        choiceRows.forEach((row) => {
            const deleteCheckbox = row.querySelector("input[type='checkbox'][name$='-DELETE']");
            if (!deleteCheckbox || !deleteCheckbox.checked) {
                count++;
            }
        });
        return count;
    }

    function validateRow(questionTbody) {
        const questionType = questionTbody.querySelector("select[name$='-question_type']")?.value;
        const minInput = questionTbody.querySelector("input[name$='-min_choices']");
        const maxInput = questionTbody.querySelector("input[name$='-max_choices']");
        const warningsInput = questionTbody.querySelector("textarea[name$='-warnings']");

        const isMulti = questionType === "multi";
        [
            questionTbody.querySelector("td.field-min_choices"),
            questionTbody.querySelector("td.field-max_choices"),
            questionTbody.querySelector("td.field-warnings"),
        ].forEach(td => {
            if (td) td.style.visibility = isMulti ? "visible" : "hidden";
        });


        questionTbody.querySelectorAll(".question-warning").forEach(el => el.remove());

        if (questionType !== "multi") return;

        const minVal = minInput?.value.trim();
        const maxVal = maxInput?.value.trim();
        const min = minVal !== "" ? parseInt(minVal) : null;
        const max = maxVal !== "" ? parseInt(maxVal) : null;
        const choiceCount = getChoiceCount(questionTbody);
        const adminWarning = warningsInput?.value.trim();

        const warnings = [];

        if (min !== null && min < 0) warnings.push("Min choices cannot be negative.");
        if (max !== null && max < 0) warnings.push("Max choices cannot be negative.");
        if (min !== null && max !== null && min > max) warnings.push("Min choices cannot exceed max choices.");
        if (min !== null && choiceCount < min) warnings.push(`At least ${min} choices are required.`);
        if (max !== null && choiceCount > max) warnings.push(`No more than ${max} choices are allowed.`);

        if (warnings.length === 0) return;
    }

    function getQuestionTbody(el) {
        const tbody = el.closest("tbody[id^='question_set-']");
        if (!tbody || tbody.id.includes("choices") || tbody.id.includes("empty")) return null;
        return tbody;
    }

    function attachListeners() {
        document.querySelectorAll([
            "select[name$='-question_type']",
            "input[name$='-min_choices']",
            "input[name$='-max_choices']",
            "input[name$='-DELETE']",
            "textarea[name$='-warnings']"
        ].join(", ")).forEach(el => {
            if (el.dataset.warningListenerAttached) return;
            el.dataset.warningListenerAttached = "true";
            el.addEventListener("change", () => {
                const tbody = getQuestionTbody(el);
                if (tbody) validateRow(tbody);
            });
            el.addEventListener("input", () => {
                const tbody = getQuestionTbody(el);
                if (tbody) validateRow(tbody);
            });
        });
    }

    function initAll() {
        document.querySelectorAll("tbody[id^='question_set-']").forEach(tbody => {
            if (!tbody.id.includes("choices") && !tbody.id.includes("empty")) {
                validateRow(tbody);
            }
        });
        attachListeners();
    }

    const observer = new MutationObserver(() => {
        attachListeners();
        document.querySelectorAll("tbody[id^='question_set-']").forEach(tbody => {
            if (!tbody.id.includes("choices") && !tbody.id.includes("empty")) {
                if (!tbody.dataset.initialized) {
                    tbody.dataset.initialized = "true";
                    validateRow(tbody);
                }
            }
        });
    });

    observer.observe(document.body, { childList: true, subtree: true });

    initAll();
});