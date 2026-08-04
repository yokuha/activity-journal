-- Render Unicode emoji as Twemoji artwork in LaTeX output.

local bmp_emoji = {
  [0x2600] = true, [0x2601] = true, [0x2602] = true, [0x2603] = true,
  [0x260E] = true, [0x2611] = true, [0x2614] = true, [0x2615] = true,
  [0x2618] = true, [0x261D] = true, [0x2620] = true, [0x2622] = true,
  [0x2623] = true, [0x2626] = true, [0x262A] = true, [0x262E] = true,
  [0x262F] = true, [0x2638] = true, [0x2639] = true, [0x263A] = true,
  [0x2640] = true, [0x2642] = true, [0x265F] = true, [0x2660] = true,
  [0x2663] = true, [0x2665] = true, [0x2666] = true, [0x2668] = true,
  [0x267B] = true, [0x267E] = true, [0x267F] = true, [0x2692] = true,
  [0x2693] = true, [0x2694] = true, [0x2695] = true, [0x2696] = true,
  [0x2697] = true, [0x2699] = true, [0x269B] = true, [0x269C] = true,
  [0x26A0] = true, [0x26A1] = true, [0x26A7] = true, [0x26AA] = true,
  [0x26AB] = true, [0x26B0] = true, [0x26B1] = true, [0x26BD] = true,
  [0x26BE] = true, [0x26C4] = true, [0x26C5] = true, [0x26C8] = true,
  [0x26CE] = true, [0x26CF] = true, [0x26D1] = true, [0x26D3] = true,
  [0x26D4] = true, [0x26E9] = true, [0x26EA] = true, [0x26F0] = true,
  [0x26F1] = true, [0x26F2] = true, [0x26F3] = true, [0x26F4] = true,
  [0x26F5] = true, [0x26F7] = true, [0x26F8] = true, [0x26F9] = true,
  [0x26FA] = true, [0x26FD] = true, [0x2702] = true, [0x2705] = true,
  [0x2708] = true, [0x2709] = true, [0x270A] = true, [0x270B] = true,
  [0x270C] = true, [0x270D] = true, [0x270F] = true, [0x2712] = true,
  [0x2714] = true, [0x2716] = true, [0x271D] = true, [0x2721] = true,
  [0x2728] = true, [0x2733] = true, [0x2734] = true, [0x2744] = true,
  [0x2747] = true, [0x274C] = true, [0x274E] = true, [0x2753] = true,
  [0x2754] = true, [0x2755] = true, [0x2757] = true, [0x2763] = true,
  [0x2764] = true, [0x2795] = true, [0x2796] = true, [0x2797] = true,
  [0x27A1] = true, [0x27B0] = true, [0x27BF] = true, [0x2B05] = true,
  [0x2B06] = true, [0x2B07] = true, [0x2B1B] = true, [0x2B1C] = true,
  [0x2B50] = true, [0x2B55] = true, [0x3030] = true, [0x303D] = true,
  [0x3297] = true, [0x3299] = true,
}

for codepoint = 0x2648, 0x2653 do
  bmp_emoji[codepoint] = true
end

local function is_emoji_base(codepoint)
  return bmp_emoji[codepoint]
    or (codepoint >= 0x1F000 and codepoint <= 0x1FAFF)
end

local function is_modifier(codepoint)
  return codepoint >= 0x1F3FB and codepoint <= 0x1F3FF
end

local function characters(text)
  local result = {}
  for position, codepoint in utf8.codes(text) do
    local next_position = utf8.offset(text, 2, position) or (#text + 1)
    table.insert(result, {
      codepoint = codepoint,
      text = text:sub(position, next_position - 1),
    })
  end
  return result
end

local function twemoji_name(cluster)
  local has_joiner = false
  local has_keycap = false
  for _, item in ipairs(cluster) do
    has_joiner = has_joiner or item.codepoint == 0x200D
    has_keycap = has_keycap or item.codepoint == 0x20E3
  end

  local parts = {}
  for _, item in ipairs(cluster) do
    if item.codepoint ~= 0xFE0E
      and (item.codepoint ~= 0xFE0F or has_joiner or has_keycap) then
      table.insert(parts, string.format('%x', item.codepoint))
    end
  end
  return table.concat(parts, '-')
end

local function append_text(output, buffer)
  if #buffer > 0 then
    table.insert(output, pandoc.Str(table.concat(buffer)))
    for index = #buffer, 1, -1 do
      buffer[index] = nil
    end
  end
end

function Str(element)
  if not FORMAT:match('latex') then
    return nil
  end

  local input = characters(element.text)
  local output = pandoc.List()
  local buffer = {}
  local index = 1

  while index <= #input do
    local item = input[index]
    if item.codepoint == 0x279E then
      append_text(output, buffer)
      output:insert(pandoc.RawInline('latex', '\\ensuremath{\\longrightarrow}'))
      index = index + 1
    elseif is_emoji_base(item.codepoint) then
      append_text(output, buffer)
      local cluster = {item}
      index = index + 1

      if item.codepoint >= 0x1F1E6 and item.codepoint <= 0x1F1FF
        and index <= #input
        and input[index].codepoint >= 0x1F1E6
        and input[index].codepoint <= 0x1F1FF then
        table.insert(cluster, input[index])
        index = index + 1
      end

      while index <= #input
        and (input[index].codepoint == 0xFE0E
          or input[index].codepoint == 0xFE0F
          or is_modifier(input[index].codepoint)) do
        table.insert(cluster, input[index])
        index = index + 1
      end

      while index <= #input and input[index].codepoint == 0x200D do
        table.insert(cluster, input[index])
        index = index + 1
        if index <= #input then
          table.insert(cluster, input[index])
          index = index + 1
        end
        while index <= #input
          and (input[index].codepoint == 0xFE0E
            or input[index].codepoint == 0xFE0F
            or is_modifier(input[index].codepoint)) do
          table.insert(cluster, input[index])
          index = index + 1
        end
      end

      output:insert(pandoc.RawInline(
        'latex',
        '\\protect\\texttwemoji{' .. twemoji_name(cluster) .. '}'
      ))
    else
      table.insert(buffer, item.text)
      index = index + 1
    end
  end

  append_text(output, buffer)
  if #output == 1 and output[1].t == 'Str' then
    return nil
  end
  return output
end
