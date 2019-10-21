import dayjs from 'dayjs';

// props to https://stackoverflow.com/questions/15900485/correct-way-to-convert-size-in-bytes-to-kb-mb-gb-in-javascript
export const bytes = (bytes, decimals = 2) => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

export const datetime = (isotime) => {
  return dayjs(isotime).format('YYYY-MM-DD HH:mm:ss')
}

export const timespan = (seconds) => {
  const base = dayjs(0);
  const diffBase = base.add(seconds, 'seconds');
  const hours = diffBase.diff(base, 'hours');
  const minutes = diffBase.diff(base, 'minutes') % 60;
  const secs = diffBase.diff(base, 'seconds') % 60;
  const makePlural = (value, base) => {
    return value > 1 ? `${base}s` : base;
  }
  let result = '';
  if (hours > 0) {
    result += `${hours} ${makePlural(hours, 'hour')}, `;
  }
  if (hours || (!hours && minutes)) {
    result += `${minutes} ${makePlural(minutes, 'minute')}`;
    if ((!hours && minutes)) {
      result += `, `;
    }
  }
  if (!hours) {
    result += `${secs} ${makePlural(secs, 'second')}`;
  }
  return result;
}

export default {
  bytes,
  datetime,
  timespan,
}