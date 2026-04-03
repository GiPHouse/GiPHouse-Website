document.addEventListener("DOMContentLoaded", () => {
    function validateQuestionRow(questionTbody) {
        
        const questionType = questionTbody.querySelector("select[name$='-question_type']")?.value;

        if (!questionType) return;

        const choicesPanel = questionTbody.querySelector("tr.djn-tr:not(.form-row)");

        const isMulti = questionType === "multi";
        const isChoice = questionType === "choice";
        const isFollowUp = isFollowUpTbody(questionTbody);

        [
            questionTbody.querySelector("td.field-min_choices"),
            questionTbody.querySelector("td.field-max_choices"),
            questionTbody.querySelector("td.field-warnings"),
        ].forEach(td => {
            if (td) td.style.visibility = isMulti ? "visible" : "hidden";
        });

        const parentChoiceTd = questionTbody.querySelector("td.field-parent_choice");
        if (parentChoiceTd) {
            parentChoiceTd.style.display = isFollowUp ? "" : "none";
        }

        if (choicesPanel) {
            choicesPanel.style.display = (isMulti || isChoice) ? "" : "none";
        }
    }

    function validateChoiceRow(choiceTbody) {

        const followUpCheckBox = choiceTbody.querySelector("input[name$='-follow_up']");
        const followUpPanel = choiceTbody.querySelector("tr.djn-tr:not(.form-row)");
        const followUpTd = choiceTbody.querySelector("td.field-follow_up");

        console.log("Validating choice row:", choiceTbody);

        console.log("followUpCheckBox:", followUpCheckBox);
        console.log("followUpPanel:", followUpPanel);
        console.log("followUpTd:", followUpTd);

        const parentQuestionTbody = choiceTbody.closest("tbody[data-inline-model='registrations-question']");
        const questionType = parentQuestionTbody?.querySelector("select[name$='-question_type']")?.value;

        const isChoice = questionType === "choice";
        const parentIsFollowUp = isFollowUpTbody(parentQuestionTbody);

        console.log("Parent question tbody:", parentQuestionTbody);
        console.log("Parent question type:", questionType);
        console.log("isChoice:", isChoice);
        console.log("parentIsFollowUp:", parentIsFollowUp);

        if (followUpTd) {
            followUpTd.style.visibility = (isChoice && !parentIsFollowUp) ? "visible" : "hidden";
        }

        if (followUpCheckBox && followUpPanel) {
            followUpPanel.style.display = followUpCheckBox.checked ? "" : "none";
        }
    }

    function isFollowUpTbody(tbody) {
        return tbody.id.includes("follow_up_questions");
    }

    function getQuestionTbody(el) {
        const tbody = el.closest("tbody[data-inline-model='registrations-question']");
        if (!tbody || tbody.id.includes("empty")) return null;
        return tbody;
    }

    function getChoiceTbody(el) {
        const tbody = el.closest("tbody[data-inline-model='registrations-questionchoice']");
        if (!tbody || tbody.id.includes("empty")) return null;
        return tbody;
    }

    function attachListeners() {
        document.querySelectorAll("select[name$='-question_type']").forEach(el => {
            if (el.dataset.warningListenerAttached) return;
            el.dataset.warningListenerAttached = "true";
            el.addEventListener("change", () => {
                const tbody = getQuestionTbody(el);
                if (tbody) validateQuestionRow(tbody);
            });
        });

        document.querySelectorAll("input[name$='-follow_up']").forEach(el => {
            if (el.dataset.followUpListenerAttached) return;
            el.dataset.followUpListenerAttached = "true";
            el.addEventListener("change", () => {
                const tbody = getChoiceTbody(el);
                if (tbody) validateChoiceRow(tbody);
            });
        });
    }

    function initAll() {
        document.querySelectorAll("tbody[data-inline-model='registrations-question']").forEach(tbody => {
            if (!tbody.id.includes("empty")) {
                validateQuestionRow(tbody);
            }
        });

        document.querySelectorAll("tbody[data-inline-model='registrations-questionchoice']").forEach(tbody => {
            if (!tbody.id.includes("empty")) {
                validateChoiceRow(tbody);
            }
        });

        attachListeners();
    }

    const observer = new MutationObserver(() => {
        attachListeners();

        document.querySelectorAll("tbody[data-inline-model='registrations-question']").forEach(tbody => {
            if (!tbody.dataset.initialized && !tbody.id.includes("empty")) {
                    tbody.dataset.initialized = "true";
                    validateQuestionRow(tbody);
                }
            }
        );

        document.querySelectorAll("tbody[data-inline-model='registrations-questionchoice']").forEach(tbody => {
            if (!tbody.dataset.initialized && !tbody.id.includes("empty")) {
                tbody.dataset.followUpInitialized = "true";
                validateChoiceRow(tbody);
            }
        });
    });

    observer.observe(document.body, { childList: true, subtree: true });

    initAll();
});