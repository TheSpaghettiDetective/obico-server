export function calculateGrade(score) {
  if (score >= 80) {
    return {
      grade: 'A',
      gradeTitle: 'A - Flawless First Layer',
      gradeAccent: 'text-success',
      gradeRemarks: "You have got a perfect first layer! Way to go!",
      gradeSuggestion: [],
    }
  } else if (score >= 60) {
    return {
      grade: 'B',
      gradeTitle: 'B - Barely a Blemish, Bravo!',
      gradeAccent: 'text-success',
      gradeRemarks: "You’re first layer is almost perfect! The risk of the first layer to cause  a failure later is VERY LOW.",
      gradeSuggestion: [
        "Minor under-extrusion.",
        "Minor over-extrusion.",
        "Suboptimal z-offset setting that causes the material to not bond perfectly.",
        "Uneven print bed coupled with suboptimal auto-bed-leveling.",
        "Other problems that cause the first layer to have defects."
      ],
    }
  } else if (score >= 40) {
    return {
      grade: 'C',
      gradeTitle: 'C - Okay First Layer',
      gradeAccent: 'text-warning',
      gradeRemarks: "The risk for the first layer to cause your print to fail later is LOW. However, if you want a perfect bottom surface finish and structural strength, you can stop the print, perfect your first layer, and restart the print.",
      gradeSuggestion: [
        "Under-extrusion.",
        "Over-extrusion.",
        "Suboptimal z-offset setting that causes the material to not bond perfectly.",
        "Contaminated print bed that causes the material in some areas to slightly bubble or wrap.",
        "Uneven print bed coupled with suboptimal auto-bed-leveling.",
        "Other problems that cause the first layer to have defects."
      ],
    }
  } else if (score >= 20) {
    return {
      grade: 'D',
      gradeTitle: 'D - Definitely Needs Tuning',
      gradeAccent: 'text-danger',
      gradeRemarks: "It looks like your printer has run into some trouble on the first layer. The risk for the first layer to cause your print to failure later is MEDIUM. Although these first layer issues probably won't cause the print to fail later, you should consider fixing them and restarting the print, especially if you want to have a good bottom surface finish and structural strength.",
      gradeSuggestion: [
        "Significant under-extrusion.",
        "Uneven print bed coupled with suboptimal auto-bed-leveling.",
        "Contaminated print bed that causes the material in some areas to bubble or wrap.",
        "Other problems that cause the first layer to show serious defects."
      ],
    }
  } else {
    return {
      grade: 'F',
      gradeTitle: 'F - First Layer Fail',
      gradeAccent: 'text-danger',
      gradeRemarks: "It looks like your printer has run into some trouble on the first layer. The risk for the first layer to cause your print to failure later is HIGH. I recommend you stop the print now and fix the problem.",
      gradeSuggestion: [
        "Serious bed-leveling problems that cause material to detach from the print bed.",
        "Wrong/suboptimal z-offset setting.",
        "Serious bubbling or wrapping.",
        "Other problems that will probably cause the print to fail later in the process."
      ]
    }
  }
}