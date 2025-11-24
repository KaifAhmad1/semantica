# Bot Features for Issues and Discussions

This document describes the minimal, conservative bot features that help users with issues and discussions.

## Issue Helper Bot (`.github/workflows/issue-bot.yml`)

### Features

#### 1. Conservative Auto-labeling
- **Trigger**: When a new issue is opened
- **Action**: Only adds labels for **clear, explicit** cases
- **Labels**:
  - `bug` - Only if title starts with "bug:" or "[bug]" OR has multiple bug indicators
  - `enhancement` - Only if explicitly mentions "feature request" or title starts with "feature:" or "[feature]"
  - `documentation` - Only if explicitly mentions "documentation issue" or title starts with "docs:"
  - `security` - Only if explicitly mentions "security issue" or title starts with "security:"
  - `needs-triage` - Only if issue body is very short (< 50 chars) and no other labels match
- **Philosophy**: Only labels when it's very clear - avoids false positives

#### 2. Help on Request Only
- **Trigger**: When an issue contains `/help` in title or body
- **Action**: Provides helpful resources and links
- **Note**: Only responds when explicitly requested - no automatic responses

## Discussion Helper Bot (`.github/workflows/discussion-bot.yml`)

### Features

#### 1. Mark as Answered (Manual)
- **Trigger**: When a maintainer comments `/answered` on a discussion
- **Action**: Marks the discussion as answered
- **Note**: Only works for repository members/owners/collaborators
- **Philosophy**: Completely manual - maintainer decides when to mark as answered

## How It Works

Both bots use GitHub Actions workflows that:
- Run only on specific, conservative triggers
- Use GitHub's API for minimal actions (labeling, marking answered)
- Use strict pattern matching - only for very clear cases
- **No automatic responses** - only responds when explicitly requested

## Safety Features

- **Minimal automation**: Only labels very clear cases, no automatic responses
- **No external services**: All bots run using GitHub Actions only
- **Manual control**: Most actions require explicit triggers
- **Conservative matching**: Only acts on very clear patterns
- **Easy to disable**: Can be disabled in repository settings

## Customization

To customize bot behavior:

1. **Modify keywords**: Edit the regex patterns in the workflow files
2. **Change responses**: Update the response text in the scripts
3. **Add new features**: Extend the workflows with additional checks

## Disabling Bots

To temporarily disable a bot:
1. Go to repository Settings → Actions → Workflows
2. Find the bot workflow
3. Click "..." → Disable workflow

Or comment out the workflow file in `.github/workflows/`

## Best Practices

1. **Review bot comments**: Ensure they're helpful and accurate
2. **Update responses**: Keep documentation links current
3. **Monitor behavior**: Check that labels are applied correctly
4. **Community feedback**: Adjust based on user feedback

---

**Note**: These bots are designed to be helpful assistants, not replacements for human interaction. They provide initial guidance, but community members and maintainers provide the real support!

